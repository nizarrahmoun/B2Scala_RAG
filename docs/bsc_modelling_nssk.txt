package bscala.bsc_program

import bscala.bsc_data._
import bscala.bsc_agent._
import bscala.bsc_runner._
import bscala.bsc_settings._
import bscala.bsc_formula._

/** Needham–Schroeder Symmetric (NSSK), using only core B2Scala primitives. */
object BSC_modelling_NSSK extends App {
  /////////////////////////////  DATA  /////////////////////////////
  val alice = Token("Alice_as_agent")
  val bob   = Token("Bob_as_agent")
  val kdc   = Token("KDC_as_agent")

  val kAS = Token("kAS_shared")
  val kBS = Token("kBS_shared")

  val NA = Token("NA")

  // Shapes
  case class pair(a: SI_Term, b: SI_Term) extends SI_Term
  case class senc(m: SI_Term, k: SI_Term) extends SI_Term
  case class message(agS: SI_Term, agR: SI_Term, payload: SI_Term) extends SI_Term

  case class a_accepts(b: SI_Term, kab: SI_Term) extends SI_Term
  case class b_accepts(a: SI_Term, kab: SI_Term) extends SI_Term

  val KAB = Token("KAB_session_key")

  /////////////////////////////  AGENTS  /////////////////////////////
  val Alice = Agent {
    tell( message(alice, kdc, Token("REQ_A_B_NA")) ) *
    get ( message(kdc, alice, pair(senc(pair(KAB, NA), kAS), senc(pair(KAB, alice), kBS))) ) *
    tell( message(alice, bob,  senc(pair(KAB, alice), kBS)) ) *
    tell( message(alice, bob,  senc(NA, KAB)) ) *
    get ( message(bob,   alice, senc(NA, KAB)) ) *
    tell( a_accepts(bob, KAB) )
  }

  val Bob = Agent {
    get ( message(alice, bob, senc(pair(KAB, alice), kBS)) ) *
    get ( message(alice, bob, senc(NA, KAB)) ) *
    tell( message(bob,   alice, senc(NA, KAB)) ) *
    tell( b_accepts(alice, KAB) )
  }

  val KDC_Agent = Agent {
    val NAq = Token("NA_query")
    get ( message(alice, kdc, Token("REQ_A_B_NA")) ) *
    tell( message(kdc, alice, pair(senc(pair(KAB, NAq), kAS), senc(pair(KAB, alice), kBS))) )
  }

  /////////////////////////////  FORMULA & EXEC /////////////////////////////
  val end = bf( a_accepts(bob, KAB) )
  val boot = not( bf( b_accepts(alice, KAB) ) )
  val F: BHM_Formula = bHM { (boot * F) + end }

  val Protocol = Agent { Alice || (Bob || KDC_Agent) }
  new BSC_Runner_BHM().execute(Protocol, F)
}
