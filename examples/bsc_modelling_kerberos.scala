package bscala.bsc_program

import bscala.bsc_data._
import bscala.bsc_agent._
import bscala.bsc_runner._
import bscala.bsc_settings._
import bscala.bsc_formula._

/** Kerberos (AS + TGS + AP), simplified, using only core B2Scala primitives. */
object BSC_modelling_Kerberos extends App {
  /////////////////////////////  DATA  /////////////////////////////
  val c   = Token("Client_as_agent")
  val s   = Token("Server_as_agent")
  val as  = Token("AS_as_agent")
  val tgs = Token("TGS_as_agent")

  val kC   = Token("kC_shared_C_AS")
  val kS   = Token("kS_shared_S_TGS")
  val kTGS = Token("kTGS_shared_AS_TGS")

  // Shapes
  case class pair(a: SI_Term, b: SI_Term) extends SI_Term
  case class senc(m: SI_Term, k: SI_Term) extends SI_Term
  case class message(agS: SI_Term, agR: SI_Term, payload: SI_Term) extends SI_Term

  case class c_has_st(c: SI_Term, s: SI_Term, kcs: SI_Term) extends SI_Term
  case class s_accepts(c: SI_Term, kcs: SI_Term) extends SI_Term

  val KTGS = Token("KTGS_session_C_TGS")
  val KCS  = Token("KCS_session_C_S")
  val NC   = Token("NC_nonce")

  /////////////////////////////  AGENTS  /////////////////////////////
  val Client = Agent {
    tell( message(c, as, Token("AS_REQ")) ) *
    get ( message(as, c, pair(senc(pair(KTGS, NC), kC), senc(pair(KTGS, c), kTGS))) ) *
    tell( message(c, tgs, Token("TGS_REQ")) ) *
    get ( message(tgs, c, pair(senc(KCS, KTGS), senc(pair(KCS, c), kS))) ) *
    tell( message(c, s, pair(senc(pair(KCS, c), kS), senc(Token("authC"), KCS))) ) *
    get ( message(s, c, senc(Token("ok"), KCS)) ) *
    tell( c_has_st(c, s, KCS) )
  }

  val ASrole = Agent {
    val NCq = Token("NC_query")
    tell( message(as, c, pair(senc(pair(KTGS, NCq), kC), senc(pair(KTGS, c), kTGS))) )
  }

  val TGSrole = Agent {
    tell( message(tgs, c, pair(senc(KCS, KTGS), senc(pair(KCS, c), kS))) )
  }

  val Server = Agent {
    val KCSq = Token("KCS_query")
    get ( message(c, s, pair(senc(pair(KCSq, c), kS), senc(Token("authC"), KCSq))) ) *
    tell( message(s, c, senc(Token("ok"), KCSq)) ) *
    tell( s_accepts(c, KCSq) )
  }

  /////////////////////////////  FORMULA & EXEC /////////////////////////////
  val end = bf( c_has_st(c, s, KCS) )
  val boot = not( bf( s_accepts(c, KCS) ) )
  val F: BHM_Formula = bHM { (boot * F) + end }

  val Protocol = Agent { Client || (ASrole || (TGSrole || Server)) }
  new BSC_Runner_BHM().execute(Protocol, F)
}
