package bscala.bsc_program

import bscala.bsc_data._
import bscala.bsc_agent._
import bscala.bsc_runner._
import bscala.bsc_settings._
import bscala.bsc_formula._

/** TLS 1.3 with a simple Dolev–Yao forwarder attacker. */
object BSC_modelling_TLS13_withAttacker extends App {
  /////////////////////////////  DATA  /////////////////////////////
  val client = Token("Client_as_agent")
  val server = Token("Server_as_agent")
  val mallory = Token("Mallory_as_intruder")

  val pkS = Token("Server_public_key")
  val skS = Token("Server_private_key")

  val tls13 = Token("label_tls13")
  val client_label = Token("label_client_finished")
  val g = Token("g_base")

  val x_eph = Token("x_ephemeral_client")
  val y_eph = Token("y_ephemeral_server")
  val nc    = Token("client_nonce")

  // Message/crypto shapes
  case class pair(a: SI_Term, b: SI_Term) extends SI_Term
  case class hash(x: SI_Term) extends SI_Term
  case class exp(base: SI_Term, exponent: SI_Term) extends SI_Term
  case class dh(x: SI_Term, gy: SI_Term) extends SI_Term
  case class kdf(secret: SI_Term, label: SI_Term) extends SI_Term
  case class prf(k: SI_Term, label: SI_Term) extends SI_Term
  case class sign(m: SI_Term, sk: SI_Term) extends SI_Term
  case class verify(sig: SI_Term, m: SI_Term, pk: SI_Term) extends SI_Term

  case class client_hello(ga: SI_Term, ncli: SI_Term) extends SI_Term
  case class server_hello(gb: SI_Term, sig: SI_Term, cert: SI_Term) extends SI_Term
  case class finished(tag: SI_Term, prfval: SI_Term) extends SI_Term

  case class message(agS: SI_Term, agR: SI_Term, payload: SI_Term) extends SI_Term

  case class client_end_tls13(pks: SI_Term, ms: SI_Term) extends SI_Term
  case class server_begin_tls13(pks: SI_Term, ms: SI_Term) extends SI_Term

  def transcript_for_sig(ga: SI_Term, gb: SI_Term, ncli: SI_Term): SI_Term =
    hash( pair(ga, pair(gb, pair(ncli, tls13))) )

  /////////////////////////////  AGENTS  /////////////////////////////
  val Client = Agent {
    val ga = exp(g, x_eph)
    val gb = exp(g, y_eph)
    val ms = kdf(dh(x_eph, gb), tls13)
    val sig = sign(transcript_for_sig(ga, gb, nc), skS)

    tell( message(client, server, client_hello(ga, nc)) ) *
    get ( message(server, client, server_hello(gb, sig, pkS)) ) *
    ask( verify(sig, transcript_for_sig(ga, gb, nc), pkS) ) *
    tell( client_end_tls13(pkS, ms) ) *
    tell( message(client, server, finished(client_label, prf(ms, client_label))) )
  }

  val Server = Agent {
    val ga = exp(g, x_eph)
    val gb = exp(g, y_eph)
    val ms = kdf(dh(y_eph, ga), tls13)
    val sig = sign(transcript_for_sig(ga, gb, nc), skS)

    get ( message(client, server, client_hello(ga, nc)) ) *
    tell( message(server, client, server_hello(gb, sig, pkS)) ) *
    tell( server_begin_tls13(pkS, ms) ) *
    get ( message(client, server, finished(client_label, prf(ms, client_label))) )
  }

  /////////////////////////////  ATTACKER  /////////////////////////////
  // Forwarder that removes messages then re-emits them unchanged (MITM relay)
  lazy val Attacker: BSC_Agent = Agent {
    (
      get( message(client, server, client_hello(exp(g, x_eph), nc)) ) *
      tell( message(client, server, client_hello(exp(g, x_eph), nc)) ) *
      Attacker
    ) + (
      get( message(server, client, server_hello(exp(g, y_eph), sign(transcript_for_sig(exp(g, x_eph), exp(g, y_eph), nc), skS), pkS)) ) *
      tell( message(server, client, server_hello(exp(g, y_eph), sign(transcript_for_sig(exp(g, x_eph), exp(g, y_eph), nc), skS), pkS)) ) *
      Attacker
    ) + (
      get( message(client, server, finished(client_label, prf(kdf(dh(x_eph, exp(g, y_eph)), tls13), client_label))) ) *
      tell( message(client, server, finished(client_label, prf(kdf(dh(x_eph, exp(g, y_eph)), tls13), client_label))) ) *
      Attacker
    )
  }

  /////////////////////////////  LOGIC (BHM)  /////////////////////////////
  // Liveness-style: eventually client_end occurs. With attacker present, this still should hold.
  val End = bf( client_end_tls13(pkS, kdf(dh(x_eph, exp(g, y_eph)), tls13)) )
  val Boot = not( bf( server_begin_tls13(pkS, kdf(dh(y_eph, exp(g, x_eph)), tls13)) ) )
  val F: BHM_Formula = bHM { (Boot * F) + End }

  /////////////////////////////  EXECUTION  /////////////////////////////
  val Protocol = Agent { Client || Server || Attacker }
  new BSC_Runner_BHM().execute(Protocol, F)
}
