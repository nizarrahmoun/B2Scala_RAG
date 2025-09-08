package bscala.bsc_program

import bscala.bsc_data._
import bscala.bsc_agent._
import bscala.bsc_runner._
import bscala.bsc_settings._
import bscala.bsc_formula._

/** Otway–Rees with a forwarder attacker. */
object BSC_modelling_OtwayRees_withAttacker extends App {
  /////////////////////////////  DATA  /////////////////////////////
  val alice = Token("Alice_as_agent")
  val bob   = Token("Bob_as_agent")
  val serv  = Token("Server_as_agent")

  val kAS = Token("kAS_shared")
  val kBS = Token("kBS_shared")

  val NA = Token("NA")
  val NB = Token("NB")
  val KAB = Token("KAB_session")

  case class pair(a: SI_Term, b: SI_Term) extends SI_Term
  case class senc(m: SI_Term, k: SI_Term) extends SI_Term
  case class message(agS: SI_Term, agR: SI_Term, payload: SI_Term) extends SI_Term

  case class a_accepts(b: SI_Term, kab: SI_Term) extends SI_Term
  case class b_accepts(a: SI_Term, kab: SI_Term) extends SI_Term

  /////////////////////////////  AGENTS  /////////////////////////////
  val Alice = Agent {
    tell( message(alice, bob, Token("M1_A_B_NA")) ) *
    get ( message(serv, alice, senc(pair(KAB, NA), kAS)) ) *
    tell( a_accepts(bob, KAB) )
  }

  val Bob = Agent {
    tell( message(bob, serv, pair(senc(Token("A_B_NA"), kAS), senc(Token("A_B_NB"), kBS))) ) *
    get ( message(serv, bob, senc(pair(KAB, NB), kBS)) ) *
    tell( b_accepts(alice, KAB) )
  }

  val Server = Agent {
    val NAq = Token("NA_query"); val NBq = Token("NB_query")
    get ( message(bob, serv, pair(senc(Token("A_B_NA"), kAS), senc(Token("A_B_NB"), kBS))) ) *
    tell( message(serv, bob,   senc(pair(KAB, NBq), kBS)) ) *
    tell( message(serv, alice, senc(pair(KAB, NAq), kAS)) )
  }

  /////////////////////////////  ATTACKER  /////////////////////////////
  lazy val Attacker: BSC_Agent = Agent {
    (
      get( message(alice, bob, Token("M1_A_B_NA")) ) *
      tell( message(alice, bob, Token("M1_A_B_NA")) ) *
      Attacker
    ) + (
      get( message(bob, serv, pair(senc(Token("A_B_NA"), kAS), senc(Token("A_B_NB"), kBS))) ) *
      tell( message(bob, serv, pair(senc(Token("A_B_NA"), kAS), senc(Token("A_B_NB"), kBS))) ) *
      Attacker
    ) + (
      get( message(serv, bob, senc(pair(KAB, NB), kBS)) ) *
      tell( message(serv, bob, senc(pair(KAB, NB), kBS)) ) *
      Attacker
    ) + (
      get( message(serv, alice, senc(pair(KAB, NA), kAS)) ) *
      tell( message(serv, alice, senc(pair(KAB, NA), kAS)) ) *
      Attacker
    )
  }

  /////////////////////////////  LOGIC (BHM)  /////////////////////////////
  val End = bf( a_accepts(bob, KAB) )
  val Boot = not( bf( b_accepts(alice, KAB) ) )
  val F: BHM_Formula = bHM { (Boot * F) + End }

  /////////////////////////////  EXECUTION  /////////////////////////////
  val Protocol = Agent { Alice || (Bob || Server) || Attacker }
  new BSC_Runner_BHM().execute(Protocol, F)
}
