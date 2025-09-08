package bscala.bsc_program

import bscala.bsc_data._
import bscala.bsc_agent._
import bscala.bsc_runner._
import bscala.bsc_settings._
import bscala.bsc_formula._

/** Needham–Schroeder (public key, Lowe fix) with Mallory attacker (forwarder). */
object BSC_modelling_NSL_withAttacker extends App {
  /////////////////////////////  DATA  /////////////////////////////
  val alice   = Token("Alice_as_agent")
  val bob     = Token("Bob_as_agent")
  val mallory = Token("Mallory_as_intruder")

  val pka = Token("Alice_public_key")
  val pkb = Token("Bob_public_key")

  val na = Token("NA")
  val nb = Token("NB")

  case class encrypt_i(vNonce: SI_Term, vAg: SI_Term, vKey: SI_Term) extends SI_Term
  case class encrypt_ii(vNonce: SI_Term, wNonce: SI_Term, vKey: SI_Term) extends SI_Term
  case class encrypt_iii(vNonce: SI_Term, vKey: SI_Term) extends SI_Term
  case class message(agS: SI_Term, agR: SI_Term, encM: SI_Term) extends SI_Term

  case class a_running(vAg: SI_Term) extends SI_Term
  case class b_running(vAg: SI_Term) extends SI_Term
  case class a_commit(vAg: SI_Term) extends SI_Term
  case class b_commit(vAg: SI_Term) extends SI_Term

  /////////////////////////////  AGENTS  /////////////////////////////
  val Alice = Agent {
    tell(a_running(bob)) *
    tell( message(alice, bob, encrypt_i(na, alice, pkb)) ) *
    get ( message(bob, alice, encrypt_ii(na, nb, pka)) ) *
    tell( message(alice, bob, encrypt_iii(nb, pkb)) ) *
    tell( a_commit(bob) )
  }

  val Bob = Agent {
    tell(b_running(alice)) *
    get ( message(alice, bob, encrypt_i(na, alice, pkb)) ) *
    tell( message(bob, alice, encrypt_ii(na, nb, pka)) ) *
    get ( message(alice, bob, encrypt_iii(nb, pkb)) ) *
    tell( b_commit(alice) )
  }

  /////////////////////////////  ATTACKER  /////////////////////////////
  lazy val Attacker: BSC_Agent = Agent {
    (
      get( message(alice, bob, encrypt_i(na, alice, pkb)) ) *
      tell( message(alice, bob, encrypt_i(na, alice, pkb)) ) *
      Attacker
    ) + (
      get( message(bob, alice, encrypt_ii(na, nb, pka)) ) *
      tell( message(bob, alice, encrypt_ii(na, nb, pka)) ) *
      Attacker
    ) + (
      get( message(alice, bob, encrypt_iii(nb, pkb)) ) *
      tell( message(alice, bob, encrypt_iii(nb, pkb)) ) *
      Attacker
    )
  }

  /////////////////////////////  LOGIC (BHM)  /////////////////////////////
  val InitBad = not( bf(a_running(bob)) or bf(b_running(alice)) or bf(b_commit(alice)) )
  val End     = bf( a_commit(bob) )
  val F: BHM_Formula = bHM { (InitBad * F) + End }

  /////////////////////////////  EXECUTION  /////////////////////////////
  val Protocol = Agent { Alice || Bob || Attacker }
  new BSC_Runner_BHM().execute(Protocol, F)
}
