package bscala.bsc_program

import bscala.bsc_data._
import bscala.bsc_agent._
import bscala.bsc_runner._
import bscala.bsc_settings._
import bscala.bsc_formula._

/** Yahalom protocol, using only core B2Scala primitives. */
object BSC_modelling_Yahalom extends App {
  /////////////////////////////  DATA  /////////////////////////////
  val alice = Token("Alice_as_agent")
  val bob   = Token("Bob_as_agent")
  val serv  = Token("Server_as_agent")

  val kAS = Token("kAS_shared")
  val kBS = Token("kBS_shared")

  val NA = Token("NA"); val NB = Token("NB")
  val KAB = Token("KAB_session")

  // Shapes
  case class pair(a: SI_Term, b: SI_Term) extends SI_Term
  case class senc(m: SI_Term, k: SI_Term) extends SI_Term
  case class message(agS: SI_Term, agR: SI_Term, payload: SI_Term) extends SI_Term

  case class a_accepts(b: SI_Term, kab: SI_Term) extends SI_Term
  case class b_accepts(a: SI_Term, kab: SI_Term) extends SI_Term

  /////////////////////////////  AGENTS  /////////////////////////////
  val Alice = Agent {
    tell( message(alice, bob, Token("A1_A_B_NA")) ) *
    get ( message(serv,  alice, senc(pair(KAB, NB), kAS)) ) *
    tell( message(alice, bob, senc(NB, KAB)) ) *
    tell( a_accepts(bob, KAB) )
  }

  val Bob = Agent {
    tell( message(bob, serv, Token("B2_B_A_NB_NA")) ) *
    get ( message(serv, bob, senc(pair(KAB, pair(alice, NA)), kBS)) ) *
    get ( message(alice, bob, senc(NB, KAB)) ) *
    tell( b_accepts(alice, KAB) )
  }

  val Server = Agent {
    val NAq = Token("NA_query"); val NBq = Token("NB_query")
    get ( message(bob, serv, Token("B2_B_A_NB_NA")) ) *
    tell( message(serv, alice, senc(pair(KAB, NBq), kAS)) ) *
    tell( message(serv, bob,   senc(pair(KAB, pair(alice, NAq)), kBS)) )
  }

  /////////////////////////////  FORMULA & EXEC /////////////////////////////
  val end = bf( a_accepts(bob, KAB) )
  val boot = not( bf( b_accepts(alice, KAB) ) )
  val F: BHM_Formula = bHM { (boot * F) + end }

  val Protocol = Agent { Alice || (Bob || Server) }
  new BSC_Runner_BHM().execute(Protocol, F)
}
