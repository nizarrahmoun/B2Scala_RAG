package bscala.bsc_program

import bscala.bsc_data._
import bscala.bsc_agent._
import bscala.bsc_runner._
import bscala.bsc_settings._
import bscala.bsc_formula._

/**
  * TLS 1.3 (ephemeral ECDHE, server-auth only) in your B2Scala style.
  * - Uses ONLY built-ins: Agent, tell/get/ask/nask, GSum, Tokens, BHM.
  * - We define ONLY the protocol-specific message/crypto/event case-classes as SI_Term.
  * - No custom DSL, no redefinitions of primitives.
  */
object BSC_modelling_TLS13 extends App {

  /////////////////////////////  DATA  /////////////////////////////

  // Agents
  val client = Token("Client_as_agent")
  val server = Token("Server_as_agent")

  // Server long-term keys (symbolic)
  val pkS = Token("Server_public_key")
  val skS = Token("Server_private_key")

  // Labels / constants
  val tls13 = Token("label_tls13")
  val client_label = Token("label_client_finished")
  val g = Token("g_base")

  // Fresh nonces (symbolic tokens)
  val x_eph = Token("x_ephemeral_client")
  val y_eph = Token("y_ephemeral_server")
  val nc    = Token("client_nonce")

  // ---- Structured terms for TLS13 (as SI_Term) ----
  case class pair(a: SI_Term, b: SI_Term) extends SI_Term
  case class hash(x: SI_Term) extends SI_Term
  case class exp(base: SI_Term, exponent: SI_Term) extends SI_Term // g^x
  case class dh(x: SI_Term, gy: SI_Term) extends SI_Term
  case class kdf(secret: SI_Term, label: SI_Term) extends SI_Term
  case class prf(k: SI_Term, label: SI_Term) extends SI_Term
  case class sign(m: SI_Term, sk: SI_Term) extends SI_Term
  case class verify(sig: SI_Term, m: SI_Term, pk: SI_Term) extends SI_Term

  // TLS handshake tokens
  case class client_hello(ga: SI_Term, ncli: SI_Term) extends SI_Term
  case class server_hello(gb: SI_Term, sig: SI_Term, cert: SI_Term) extends SI_Term
  case class finished(tag: SI_Term, prfval: SI_Term) extends SI_Term

  // Network envelope (kept simple like your NS example)
  case class message(agS: SI_Term, agR: SI_Term, payload: SI_Term) extends SI_Term

  // Events
  case class client_end_tls13(pks: SI_Term, ms: SI_Term) extends SI_Term
  case class server_begin_tls13(pks: SI_Term, ms: SI_Term) extends SI_Term

  // Helpers for transcript/signature
  def transcript_for_sig(ga: SI_Term, gb: SI_Term, ncli: SI_Term): SI_Term =
    hash( pair(ga, pair(gb, pair(ncli, tls13))) )

  /////////////////////////////  AGENTS  /////////////////////////////

  val Client = Agent {
    val ga = exp(g, x_eph)
    val gb = exp(g, y_eph) // pattern variable in get below (symbolic here for shape)
    val ms = kdf(dh(x_eph, gb), tls13)
    val sig = sign(transcript_for_sig(ga, gb, nc), skS)

    tell( message(client, server, client_hello(ga, nc)) ) *
    get(  message(server, client, server_hello(gb, sig, pkS)) ) *
    // Signature check modeled with ask over a Verify token
    ask( verify(sig, transcript_for_sig(ga, gb, nc), pkS) ) *
    tell( client_end_tls13(pkS, ms) ) *
    tell( message(client, server, finished(client_label, prf(ms, client_label))) )
  }

  val Server = Agent {
    val ga = exp(g, x_eph) // pattern variable in get below (symbolic here for shape)
    val gb = exp(g, y_eph)
    val ms = kdf(dh(y_eph, ga), tls13)
    val sig = sign(transcript_for_sig(ga, gb, nc), skS)

    get(  message(client, server, client_hello(ga, nc)) ) *
    tell( message(server, client, server_hello(gb, sig, pkS)) ) *
    tell( server_begin_tls13(pkS, ms) ) *
    get(  message(client, server, finished(client_label, prf(ms, client_label))) )
  }

  /////////////////////////////  (OPTIONAL) FORMULA  /////////////////////////////

  // Example BHM: eventually a client_end follows a server_begin (very light sketch).
  // NOTE: Adapt to your exact BHM style; you can refine injectivity or secrecy separately.
  val good = bf( client_end_tls13(pkS, kdf(dh(x_eph, exp(g, y_eph)), tls13)) )
  val boot = not( bf(server_begin_tls13(pkS, kdf(dh(y_eph, exp(g, x_eph)), tls13))) )

  val F: BHM_Formula = bHM {
    (boot * F) + good
  }

  /////////////////////////////  EXECUTION  /////////////////////////////

  val Protocol = Agent { Client || Server }

  val bsc_executor = new BSC_Runner_BHM
  bsc_executor.execute(Protocol, F)
}
