package bscala.bsc_program

import bscala.bsc_data._
import bscala.bsc_agent._
import bscala.bsc_runner._
import bscala.bsc_settings._
import bscala.bsc_formula._

/** Denning–Sacco with timestamps (symmetric) + forwarder attacker. */
object BSC_modelling_DenningSaccoTS_withAttacker extends App {
  /////////////////////////////  DATA  /////////////////////////////
  val alice = Token("Alice_as_agent")
  val bob   = Token("Bob_as_agent")
  val serv  = Token("Server_as_agent")
  val mallory = Token("Mallory_as_intruder")

  val kAS = Token("kAS_shared")
  val kBS = Token("kBS_shared")

  val KAB = Token("KAB_session")
  val TS  = Token("Timestamp")

  // Shapes
  case class pair(a: SI_Term, b: SI_Term) extends SI_Term
  case class senc(m: SI_Term, k: SI_Term) extends SI_Term
  case class message(agS: SI_Term, agR: SI_Term, payload: SI_Term) extends SI_Term

  case class a_accepts(b: SI_Term, kab: SI_Term) extends SI_Term
  case class b_accepts(a: SI_Term, kab: SI_Term) extends SI_Term

  /////////////////////////////  AGENTS  /////////////////////////////
  val Alice = Agent {
    tell( message(alice, serv, Token("A_to_S_with_KAB_TS")) ) *
    get ( message(serv,  alice, senc(pair(KAB, alice), kBS)) ) *
    tell( message(alice, bob,  senc(pair(KAB, alice), kBS)) ) *
    get ( message(bob,   alice, senc(Token("ok"), KAB)) ) *
    tell( a_accepts(bob, KAB) )
  }

  val Bob = Agent {
    get ( message(alice, bob, senc(pair(KAB, alice), kBS)) ) *
    tell( message(bob,   alice, senc(Token("ok"), KAB)) ) *
    tell( b_accepts(alice, KAB) )
  }

  val Server = Agent {
    tell( message(serv, alice, senc(pair(KAB, alice), kBS)) )
  }

  /////////////////////////////  ATTACKER  /////////////////////////////
  lazy val Attacker: BSC_Agent = Agent {
    (
      get( message(alice, serv, Token("A_to_S_with_KAB_TS")) ) *
      tell( message(alice, serv, Token("A_to_S_with_KAB_TS")) ) *
      Attacker
    ) + (
      get( message(serv, alice, senc(pair(KAB, alice), kBS)) ) *
      tell( message(serv, alice, senc(pair(KAB, alice), kBS)) ) *
      Attacker
    ) + (
      get( message(alice, bob, senc(pair(KAB, alice), kBS)) ) *
      tell( message(alice, bob, senc(pair(KAB, alice), kBS)) ) *
      Attacker
    ) + (
      get( message(bob, alice, senc(Token("ok"), KAB)) ) *
      tell( message(bob, alice, senc(Token("ok"), KAB)) ) *
      Attacker
    )
  }

  /////////////////////////////  LOGIC (BHM)  /////////////////////////////
  val End  = bf( a_accepts(bob, KAB) )
  val Boot = not( bf( b_accepts(alice, KAB) ) )
  val F: BHM_Formula = bHM { (Boot * F) + End }

  /////////////////////////////  EXECUTION  /////////////////////////////
  val Protocol = Agent { Alice || (Bob || Server) || Attacker }
  new BSC_Runner_BHM().execute(Protocol, F)
}
