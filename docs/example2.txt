package bscala.bsc_program

import bscala.bsc_data._
import bscala.bsc_agent._
import bscala.bsc_runner._
import bscala.bsc_settings._
import bscala.bsc_formula._

/** EMV – exemple minimal (Terminal ↔ Carte), sans temps, sans attaquant. */
object BSC_modelling_EMV_Minimal extends App {

  /////////////////////////////  DONNÉES  /////////////////////////////

  val terminal = Token("Terminal")
  val card     = Token("Card")

  // Montant (fixe pour l’exemple)
  val amount = Token("amount_10")

  // Clé carte (symbolique, jamais dans le store)
  val k_card = Token("k_card")

  // Pools finis pour l’imprévisible (UN) et le compteur ATC
  val poolUN  = List(Token("un1"), Token("un2"))
  val poolATC = List(Token("atc1"), Token("atc2"))

  // Constructeurs symboliques
  case class un(v: SI_Term)                                    extends SI_Term
  case class arqc(tag: SI_Term)                                extends SI_Term
  case class derive(k: SI_Term, atc: SI_Term)                  extends SI_Term
  case class mac(k: SI_Term, data: SI_Term)                    extends SI_Term
  case class data(un: SI_Term, atc: SI_Term, amt: SI_Term)     extends SI_Term

  // Enveloppe message
  case class msg(sender: SI_Term, receiver: SI_Term, payload: SI_Term) extends SI_Term

  // Marqueurs pour BHM
  case class t_running(vC: SI_Term) extends SI_Term
  case class c_running(vT: SI_Term) extends SI_Term
  case class t_commit(vC: SI_Term)  extends SI_Term
  case class c_commit(vT: SI_Term)  extends SI_Term

  /////////////////////////////  AGENTS  /////////////////////////////

  // Terminal : choisit UN ; envoie UN ; reçoit ARQC ; commit.
  val Terminal = Agent {
    t_running(card) *
    GSum(poolUN, vUN => {
      val P_un = un(vUN)
      tell(msg(terminal, card, P_un)) *
      GSum(poolATC, vATC => {
        val K   = derive(k_card, vATC)
        val D   = data(P_un, vATC, amount)
        val ARQ = arqc(mac(K, D))
        get(msg(card, terminal, ARQ)) *
        t_commit(card)
      })
    })
  }

  // Carte : choisit ATC ; attend UN ; renvoie ARQC ; commit.
  val Card = Agent {
    c_running(terminal) *
    GSum(poolATC, vATC => {
      GSum(poolUN, vUN => {
        val P_un = un(vUN)
        val K    = derive(k_card, vATC)
        val D    = data(P_un, vATC, amount)
        val ARQ  = arqc(mac(K, D))
        get(msg(terminal, card, P_un)) *
        tell(msg(card, terminal, ARQ)) *
        c_commit(terminal)
      })
    })
  }

  /////////////////////////////  FORMULE BHM  /////////////////////////////

  val sane_init =
    not(bf(t_commit(card)) or bf(c_commit(terminal)))

  val end_session =
    bf(t_commit(card)) and bf(c_commit(terminal))

  val F: BHM_Formula = bHM { (sane_init * F) + end_session }

  /////////////////////////////  EXÉCUTION  /////////////////////////////

  val Protocol = Agent { Terminal || Card }

  val runner = new BSC_Runner_BHM
  runner.execute(Protocol, F)
}
