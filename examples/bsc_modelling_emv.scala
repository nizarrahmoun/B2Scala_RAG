package bscala.bsc_program

import bscala.bsc_data._
import bscala.bsc_agent._
import bscala.bsc_runner._
import bscala.bsc_settings._
import bscala.bsc_formula._

/** EMV (contact) online authorization, using only core B2Scala primitives. */
object BSC_modelling_EMV extends App {
  /////////////////////////////  DATA  /////////////////////////////
  val card     = Token("Card_as_agent")
  val terminal = Token("Terminal_as_agent")
  val issuer   = Token("Issuer_as_agent")

  val kC   = Token("CardIssuer_shared_key")
  val PAN  = Token("PAN_value")

  val UN   = Token("Unpredictable_number")
  val ATC  = Token("App_Transaction_Counter")

  // Cryptographic constructors as SI_Term
  case class pair(a: SI_Term, b: SI_Term) extends SI_Term
  case class mac(m: SI_Term, k: SI_Term) extends SI_Term

  // EMV tokens
  case class arqc(pan: SI_Term, atc: SI_Term, un: SI_Term, macv: SI_Term) extends SI_Term
  case class arpc(of: SI_Term, macv: SI_Term) extends SI_Term

  // Envelope
  case class message(agS: SI_Term, agR: SI_Term, payload: SI_Term) extends SI_Term

  // Events
  case class card_arqc(pan: SI_Term, atc: SI_Term, un: SI_Term, tag: SI_Term) extends SI_Term
  case class card_accepts_arpc(pan: SI_Term, atc: SI_Term) extends SI_Term
  case class issuer_verifies_arqc(pan: SI_Term, atc: SI_Term, un: SI_Term, tag: SI_Term) extends SI_Term

  /////////////////////////////  AGENTS  /////////////////////////////

  val Card = Agent {
    val data = pair(PAN, pair(ATC, UN))
    val tag  = mac(pair(Token("ARQC"), data), kC)
    get ( message(terminal, card, UN) ) *
    tell( card_arqc(PAN, ATC, UN, tag) ) *
    tell( message(card, terminal, arqc(PAN, ATC, UN, tag)) ) *
    { val reply = mac(pair(Token("ARPC"), tag), kC)
      get ( message(terminal, card, arpc(arqc(PAN, ATC, UN, tag), reply)) ) *
      tell( card_accepts_arpc(PAN, ATC) )
    }
  }

  val Terminal = Agent {
    val verify = Token("VERIFY")
    tell( message(terminal, card, UN) ) *
    get ( message(card, terminal, arqc(PAN, ATC, UN, mac(pair(Token("ARQC"), pair(PAN, pair(ATC, UN))), kC))) ) *
    tell( message(terminal, issuer, verify) ) *
    get ( message(issuer, terminal, Token("ARPC_payload")) ) *
    tell( message(terminal, card, arpc(arqc(PAN, ATC, UN, mac(pair(Token("ARQC"), pair(PAN, pair(ATC, UN))), kC)), mac(pair(Token("ARPC"), mac(pair(Token("ARQC"), pair(PAN, pair(ATC, UN))), kC)), kC))) )
  }

  val Issuer = Agent {
    val verify = Token("VERIFY")
    get ( message(terminal, issuer, verify) ) *
    tell( issuer_verifies_arqc(PAN, ATC, UN, mac(pair(Token("ARQC"), pair(PAN, pair(ATC, UN))), kC)) ) *
    tell( message(issuer, terminal, Token("ARPC_payload")) )
  }

  /////////////////////////////  FORMULA & EXEC /////////////////////////////
  val end = bf( card_accepts_arpc(PAN, ATC) )
  val start_not = not( bf( issuer_verifies_arqc(PAN, ATC, UN, mac(pair(Token("ARQC"), pair(PAN, pair(ATC, UN))), kC)) ) )
  val F: BHM_Formula = bHM { (start_not * F) + end }

  val Protocol = Agent { Card || (Terminal || Issuer) }
  new BSC_Runner_BHM().execute(Protocol, F)
}
