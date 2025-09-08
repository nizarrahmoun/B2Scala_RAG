package bscala.bsc_program

import bscala.bsc_data._
import bscala.bsc_agent._
import bscala.bsc_runner._
import bscala.bsc_settings._
import bscala.bsc_formula._

/**
 * QUIC 1-RTT handshake (symbolic), replay-only attacker.
 * Style: B2Scala ( * sequence, + choice, || parallel, GSum enumerations )
 * Notes:
 *  - We model QUIC’s TLS 1.3 handshake minimally as: CH -> SH -> FIN_s -> FIN_c
 *  - Secrets, MACs, HKDF, etc., are symbolic constructors (no computation).
 *  - Freshness: client_random, server_random, scid/dcid chosen from finite pools.
 *  - Mallory only replays observed payloads (no forging).
 */
object BSC_modelling_QUIC_Handshake_ReplayOnly extends App {

  /////////////////////////////  DATA  /////////////////////////////

  // Parties
  val client  = Token("Client")
  val server  = Token("Server")
  val mallory = Token("Mallory")

  // Version & salts (symbolic)
  val quic_v1    = Token("quic_v1")
  val initial_s  = Token("initial_salt") // symbolic; never told to store

  // Freshness pools (finite)
  val poolCR  = List(Token("cr1"), Token("cr2"), Token("cr3")) // client random
  val poolSR  = List(Token("sr1"), Token("sr2"), Token("sr3")) // server random
  val poolDCID= List(Token("dcid1"), Token("dcid2"))           // destination connection ID (chosen by server)
  val poolSCID= List(Token("scid1"), Token("scid2"))           // source connection ID    (chosen by client)

  // Payload constructors (si-terms)
  // QUIC maps TLS to CRYPTO frames; we abstract into four phases:
  // ch  (ClientHello), sh (ServerHello), fins (ServerFinished), finc (ClientFinished)
  case class ch(v: SI_Term, scid: SI_Term, cr: SI_Term)       extends SI_Term // includes version, client SCID, client_random
  case class sh(v: SI_Term, dcid: SI_Term, sr: SI_Term)       extends SI_Term // includes version, server DCID, server_random
  case class transcript(m1: SI_Term, m2: SI_Term)             extends SI_Term
  case class hkdf_extract(salt: SI_Term, dcid: SI_Term)       extends SI_Term // initial secret binding
  case class derive_1rtt(init: SI_Term, cr: SI_Term, sr: SI_Term) extends SI_Term
  case class mac(k: SI_Term, tr: SI_Term)                     extends SI_Term
  case class fins(tag: SI_Term)                               extends SI_Term  // server Finished
  case class finc(tag: SI_Term)                               extends SI_Term  // client Finished

  // Envelope (QUIC header abstracts to sender/receiver tuple)
  case class msg(sender: SI_Term, receiver: SI_Term, payload: SI_Term) extends SI_Term

  // Markers for BHM properties
  case class c_running(vS: SI_Term) extends SI_Term
  case class s_running(vC: SI_Term) extends SI_Term
  case class c_commit(vS: SI_Term)  extends SI_Term
  case class s_commit(vC: SI_Term)  extends SI_Term

  /////////////////////////////  AGENTS  /////////////////////////////

  // Client:
  // choose SCID, CR; send CH; wait SH(DCID, SR); derive keys; wait FIN_s; send FIN_c; commit
  val Client = Agent {
    GSum(List(server, mallory), S => {
      GSum(poolSCID, vSCID => {
        GSum(poolCR, vCR => {
          val CH  = ch(quic_v1, vSCID, vCR)
          tell(c_running(S)) *
          tell(msg(client, S, CH)) *
          GSum(poolDCID, vDCID => {
            GSum(poolSR, vSR => {
              val SH   = sh(quic_v1, vDCID, vSR)
              val TR   = transcript(CH, SH)
              val IS   = hkdf_extract(initial_s, vDCID)      // initial secret binds DCID
              val K    = derive_1rtt(IS, vCR, vSR)
              val FINs = fins(mac(K, TR))
              val FINc = finc(mac(K, TR))
              get(msg(S, client, SH)) *
              get(msg(S, client, FINs)) *
              tell(msg(client, S, FINc)) *
              tell(c_commit(S))
            })
          })
        })
      })
    })
  }

  // Server:
  // wait CH(SCID, CR); choose DCID, SR; send SH; send FIN_s; wait FIN_c; commit
  val Server = Agent {
    GSum(List(client, mallory), C => {
      tell(s_running(C)) *
      GSum(poolSCID, vSCID => {
        GSum(poolCR, vCR => {
          val CHpat = ch(quic_v1, vSCID, vCR)
          get(msg(C, server, CHpat)) *
          GSum(poolDCID, vDCID => {
            GSum(poolSR, vSR => {
              val SH   = sh(quic_v1, vDCID, vSR)
              val TR   = transcript(CHpat, SH)
              val IS   = hkdf_extract(initial_s, vDCID)
              val K    = derive_1rtt(IS, vCR, vSR)
              val FINs = fins(mac(K, TR))
              val FINc = finc(mac(K, TR))
              tell(msg(server, C, SH)) *
              tell(msg(server, C, FINs)) *
              get(msg(C, server, FINc)) *
              tell(s_commit(C))
            })
          })
        })
      })
    })
  }

  // Mallory (replay-only): capture exact payloads and replay them (no forging).
  // We enumerate all payload shapes via pools and only re-emit captured terms.
  lazy val Mallory: BSC_Agent = Agent {

    // Replay ClientHello
    ( GSum(List(client, server, mallory), X => {
        GSum(List(client, server, mallory), Y => {
          GSum(List(client, server, mallory), Z => {
            GSum(poolSCID, vSCID => {
              GSum(poolCR, vCR => {
                val P = ch(quic_v1, vSCID, vCR)
                get(msg(X, Y, P)) * tell(msg(mallory, Z, P)) * Mallory
              })
            })
          })
        })
      })) +

    // Replay ServerHello
    ( GSum(List(client, server, mallory), X => {
        GSum(List(client, server, mallory), Y => {
          GSum(List(client, server, mallory), Z => {
            GSum(poolDCID, vDCID => {
              GSum(poolSR, vSR => {
                val P = sh(quic_v1, vDCID, vSR)
                get(msg(X, Y, P)) * tell(msg(mallory, Z, P)) * Mallory
              })
            })
          })
        })
      })) +

    // Replay Server Finished
    ( GSum(poolSCID, vSCID => {
        GSum(poolCR, vCR => {
          GSum(poolDCID, vDCID => {
            GSum(poolSR, vSR => {
              val CH = ch(quic_v1, vSCID, vCR)
              val SH = sh(quic_v1, vDCID, vSR)
              val TR = transcript(CH, SH)
              val IS = hkdf_extract(initial_s, vDCID)
              val K  = derive_1rtt(IS, vCR, vSR)
              val P  = fins(mac(K, TR))
              GSum(List(client, server, mallory), X => {
                GSum(List(client, server, mallory), Y => {
                  GSum(List(client, server, mallory), Z => {
                    get(msg(X, Y, P)) * tell(msg(mallory, Z, P)) * Mallory
                  })
                })
              })
            })
          })
        })
      })) +

    // Replay Client Finished
    ( GSum(poolSCID, vSCID => {
        GSum(poolCR, vCR => {
          GSum(poolDCID, vDCID => {
            GSum(poolSR, vSR => {
              val CH = ch(quic_v1, vSCID, vCR)
              val SH = sh(quic_v1, vDCID, vSR)
              val TR = transcript(CH, SH)
              val IS = hkdf_extract(initial_s, vDCID)
              val K  = derive_1rtt(IS, vCR, vSR)
              val P  = finc(mac(K, TR))
              GSum(List(client, server, mallory), X => {
                GSum(List(client, server, mallory), Y => {
                  GSum(List(client, server, mallory), Z => {
                    get(msg(X, Y, P)) * tell(msg(mallory, Z, P)) * Mallory
                  })
                })
              })
            })
          })
        })
      }))
  }

  /////////////////////////////  bHM FORMULA  /////////////////////////////

  // Sanity: no commit before running; no commit with Mallory as peer.
  val sane_init =
    not(bf(c_commit(server)) or bf(s_commit(client)) or
        bf(c_commit(mallory)) or bf(s_commit(mallory))) and
    not(bf(c_running(mallory)) or bf(s_running(mallory)))

  // End: mutual commit between intended peers
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
