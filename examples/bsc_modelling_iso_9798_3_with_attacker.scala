package bscala.bsc_program

import bscala.bsc_data._
import bscala.bsc_agent._
import bscala.bsc_runner._
import bscala.bsc_settings._
import bscala.bsc_formula._

/** ISO/IEC 9798-3 (public key challenge) + forwarder attacker. */
object BSC_modelling_ISO9798_3_withAttacker extends App {
  /////////////////////////////  DATA  /////////////////////////////
  val alice   = Token("Alice_as_agent")
  val bob     = Token("Bob_as_agent")
  val mallory = Token("Mallory_as_intruder")

  val pka = Token("Alice_public_key")
  val pkb = Token("Bob_public_key")

  val NA = Token("NA"); val NB = Token("NB")

  case class pair(a: SI_Term, b: SI_Term) extends SI_Term
  case class aenc(m: SI_Term, pk: SI_Term) extends SI_Term
  case class message(agS: SI_Term, agR: SI_Term, payload: SI_Term) extends SI_Term

  case class a_authenticates_b(na: SI_Term, nb: SI_Term) extends SI_Term
  case class b_authenticates_a(na: SI_Term) extends SI_Term

  /////////////////////////////  AGENTS  /////////////////////////////
  val Alice = Agent {
    tell( message(alice, bob, pair(pka, NA)) ) *
    get ( message(bob,   alice, aenc(pair(NB, pka), pka)) ) *
    tell( message(alice, bob, aenc(NB, pkb)) ) *
    tell( a_authenticates_b(NA, NB) )
  }

  val Bob = Agent {
    tell( message(bob,   alice, aenc(pair(NB, pka), pka)) ) *
    get ( message(alice, bob, aenc(NB, pkb)) ) *
    tell( b_authenticates_a(NA) )
  }

  /////////////////////////////  ATTACKER  /////////////////////////////
  lazy val Attacker: BSC_Agent = Agent {
    (
      get( message(alice, bob, pair(pka, NA)) ) *
      tell( message(alice, bob, pair(pka, NA)) ) *
      Attacker
    ) + (
      get( message(bob, alice, aenc(pair(NB, pka), pka)) ) *
      tell( message(bob, alice, aenc(pair(NB, pka), pka)) ) *
      Attacker
    ) + (
      get( message(alice, bob, aenc(NB, pkb)) ) *
      tell( message(alice, bob, aenc(NB, pkb)) ) *
      Attacker
    )
  }

  /////////////////////////////  LOGIC (BHM)  /////////////////////////////
  val End  = bf( a_authenticates_b(NA, NB) )
  val Boot = not( bf( b_authenticates_a(NA) ) )
  val F: BHM_Formula = bHM { (Boot * F) + End }

  /////////////////////////////  EXECUTION  /////////////////////////////
  val Protocol = Agent { Alice || Bob || Attacker }
  new BSC_Runner_BHM().execute(Protocol, F)
}
