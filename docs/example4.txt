package bscala.bsc_program

import bscala.bsc_data._
import bscala.bsc_agent._
import bscala.bsc_runner._
import bscala.bsc_settings._
import bscala.bsc_formula._

object BSC_modelling_TLS_PSK_ReplayOnly extends App {

  /////////////////////////////  DATA  /////////////////////////////

  // Parties
  val client  = Token("Client")
  val server  = Token("Server")
  val mallory = Token("Mallory")

  // PSK identity and shared key (symbolic; the key is never told to the store)
  val pskid  = Token("psk_identity")
  val psk_ab = Token("psk_ab")

  // Freshness pools (finite for model-checking)
  val poolCR = List(Token("cr1"), Token("cr2"), Token("cr3"))
  val poolSR = List(Token("sr1"), Token("sr2"), Token("sr3"))

  // Payload constructors (si-terms)
  case class ch(vCR: SI_Term, vClient: SI_Term, vPSKID: SI_Term) extends SI_Term
  case class sh(vSR: SI_Term, vServer: SI_Term)                  extends SI_Term
  case class transcript(m1: SI_Term, m2: SI_Term)                extends SI_Term
  case class derive(psk: SI_Term, vCR: SI_Term, vSR: SI_Term)    extends SI_Term
  case class mac(k: SI_Term, tr: SI_Term)                        extends SI_Term
  case class finished(side: SI_Term, tag: SI_Term)               extends SI_Term

  // Envelope
  case class msg(sender: SI_Term, receiver: SI_Term, payload: SI_Term) extends SI_Term

  // Annotations for properties
  case class c_running(vS: SI_Term) extends SI_Term
  case class s_running(vC: SI_Term) extends SI_Term
  case class c_commit(vS: SI_Term)  extends SI_Term
  case class s_commit(vC: SI_Term)  extends SI_Term

  /////////////////////////////  AGENTS  /////////////////////////////

  // Client: choose server/mallory, choose fresh cr, send CH; receive SH(sv), send FIN(c), receive FIN(s)
  val Client = Agent {
    GSum(List(server, mallory), S => {
      GSum(poolCR, vCR => {
        val CH = ch(vCR, client, pskid)
        tell(c_running(S)) *
        tell(msg(client, S, CH)) *
        GSum(poolSR, vSR => {
          val SH = sh(vSR, S)
          val TR = transcript(CH, SH)
          val K  = derive(psk_ab, vCR, vSR)
          val FINc = finished(client, mac(K, TR))
          val FINs = finished(S,      mac(K, TR))
          get(msg(S, client, SH)) *
          tell(msg(client, S, FINc)) *
          get(msg(S, client, FINs)) *
          tell(c_commit(S))
        })
      })
    })
  }

  // Server: choose peer (client/mallory), match CH(cr), choose fresh sr, send SH; receive FIN(c), send FIN(s)
  val Server = Agent {
    GSum(List(client, mallory), C => {
      tell(s_running(C)) *
      GSum(poolCR, vCR => {
        val CHpat = ch(vCR, C, pskid)
        get(msg(C, server, CHpat)) *
        GSum(poolSR, vSR => {
          val SH = sh(vSR, server)
          val TR = transcript(CHpat, SH)
          val K  = derive(psk_ab, vCR, vSR)
          val FINc = finished(C,      mac(K, TR))
          val FINs = finished(server, mac(K, TR))
          tell(msg(server, C, SH)) *
          get(msg(C, server, FINc)) *
          tell(msg(server, C, FINs)) *
          tell(s_commit(C))
        })
      })
    })
  }

  // Mallory (replay-only): intercept exact payloads and replay them; no forging of MAC/derive
  lazy val Mallory: BSC_Agent = Agent {
    // Replay ClientHello
    ( GSum(List(client, server, mallory), X => {
        GSum(List(client, server, mallory), Y => {
          GSum(List(client, server, mallory), Z => {
            GSum(poolCR, vCR => {
              val P = ch(vCR, client, pskid)
              get(msg(X, Y, P)) * tell(msg(mallory, Z, P)) * Mallory
            })
          })
        })
      })) +

    // Replay ServerHello
    ( GSum(List(client, server, mallory), X => {
        GSum(List(client, server, mallory), Y => {
          GSum(List(client, server, mallory), Z => {
            GSum(poolSR, vSR => {
              val P = sh(vSR, server)
              get(msg(X, Y, P)) * tell(msg(mallory, Z, P)) * Mallory
            })
          })
        })
      })) +

    // Replay Finished (either side), enumerating all nonce pairs
    ( GSum(List(client, server), Side => {
        GSum(poolCR, vCR => {
          GSum(poolSR, vSR => {
            val CH = ch(vCR, client, pskid)
            val SH = sh(vSR, server)
            val TR = transcript(CH, SH)
            val K  = derive(psk_ab, vCR, vSR)
            val P  = finished(Side, mac(K, TR))
            GSum(List(client, server, mallory), X => {
              GSum(List(client, server, mallory), Y => {
                GSum(List(client, server, mallory), Z => {
                  get(msg(X, Y, P)) * tell(msg(mallory, Z, P)) * Mallory
                })
              })
            })
          })
        })
      }))
  }

  /////////////////////////////  bHM FORMULA  /////////////////////////////

  // No commit before any running marker
  val sane_init =
    not(bf(c_commit(server)) or bf(s_commit(client)) or
        bf(c_commit(mallory)) or bf(s_commit(mallory))) and
    not(bf(c_running(mallory)) or bf(s_running(mallory)))

  // Mutual commit between intended peers
  val end_session =
    bf(c_commit(server)) and bf(s_commit(client))

  val F: BHM_Formula = bHM {
    (sane_init * F) + end_session
  }

  ///////////////////////  EXECUTION  /////////////////////////

  val Protocol = Agent {
    Client || Server || Mallory
  }

  val bsc_executor = new BSC_Runner_BHM
  bsc_executor.execute(Protocol, F)
}
