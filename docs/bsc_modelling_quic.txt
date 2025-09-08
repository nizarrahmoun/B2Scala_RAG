package bscala.bsc_program

import bscala.bsc_data._
import bscala.bsc_agent._
import bscala.bsc_runner._
import bscala.bsc_settings._
import bscala.bsc_formula._

/** QUIC v1 handshake bound to TLS 1.3 semantics, using only core B2Scala primitives. */
object BSC_modelling_QUIC extends App {
  /////////////////////////////  DATA  /////////////////////////////
  val client = Token("Client_as_agent")
  val server = Token("Server_as_agent")

  val pkS = Token("Server_public_key")
  val skS = Token("Server_private_key")

  val label_quic = Token("label_quic")
  val label_finished = Token("label_client_finished")
  val g = Token("g_base")

  val x_eph = Token("x_ephemeral_client")
  val y_eph = Token("y_ephemeral_server")
  val nc    = Token("client_nonce")

  val scid  = Token("source_connection_id")
  val dcid  = Token("dest_connection_id")
  val tpC   = Token("transport_params_client")
  val tpS   = Token("transport_params_server")

  // ---- Structured terms (as SI_Term) ----
  case class pair(a: SI_Term, b: SI_Term) extends SI_Term
  case class quad(a: SI_Term, b: SI_Term, c: SI_Term, d: SI_Term) extends SI_Term
  case class hash(x: SI_Term) extends SI_Term
  case class exp(base: SI_Term, exponent: SI_Term) extends SI_Term
  case class dh(x: SI_Term, gy: SI_Term) extends SI_Term
  case class kdf(secret: SI_Term, label: SI_Term) extends SI_Term
  case class prf(k: SI_Term, label: SI_Term) extends SI_Term
  case class sign(m: SI_Term, sk: SI_Term) extends SI_Term
  case class verify(sig: SI_Term, m: SI_Term, pk: SI_Term) extends SI_Term

  // TLS/QUIC tokens
  case class client_hello(ga: SI_Term, ncli: SI_Term) extends SI_Term
  case class finished(tag: SI_Term, prfval: SI_Term) extends SI_Term
  case class initial(scid: SI_Term, dcid: SI_Term, tpc: SI_Term, ch: SI_Term) extends SI_Term
  case class handshake(gb: SI_Term, tps: SI_Term, sig: SI_Term, cert: SI_Term) extends SI_Term

  // Envelope
  case class message(agS: SI_Term, agR: SI_Term, payload: SI_Term) extends SI_Term

  // Events
  case class client_end_quic(pks: SI_Term, ms: SI_Term, scid: SI_Term, dcid: SI_Term) extends SI_Term
  case class server_begin_quic(pks: SI_Term, ms: SI_Term, scid: SI_Term, dcid: SI_Term) extends SI_Term

  def sig_scope(ga: SI_Term, gb: SI_Term, sc: SI_Term, dc: SI_Term, tpc: SI_Term, tps: SI_Term): SI_Term =
    hash( quad(ga, gb, pair(sc, dc), pair(tpc, tps)) )

  /////////////////////////////  AGENTS  /////////////////////////////

  val Client = Agent {
    val ga = exp(g, x_eph)
    val gb = exp(g, y_eph) // pattern variable placeholder
    val ms = kdf(dh(x_eph, gb), label_quic)
    val sig = sign(sig_scope(ga, gb, scid, dcid, tpC, tpS), skS)

    tell( message(client, server, initial(scid, dcid, tpC, client_hello(ga, nc))) ) *
    get ( message(server, client, handshake(gb, tpS, sig, pkS)) ) *
    ask( verify(sig, sig_scope(ga, gb, scid, dcid, tpC, tpS), pkS) ) *
    tell( client_end_quic(pkS, ms, scid, dcid) ) *
    tell( message(client, server, finished(label_finished, prf(ms, label_finished))) )
  }

  val Server = Agent {
    val ga = exp(g, x_eph)
    val gb = exp(g, y_eph)
    val ms = kdf(dh(y_eph, ga), label_quic)
    val sig = sign(sig_scope(ga, gb, scid, dcid, tpC, tpS), skS)

    get ( message(client, server, initial(scid, dcid, tpC, client_hello(ga, nc))) ) *
    tell( message(server, client, handshake(gb, tpS, sig, pkS)) ) *
    tell( server_begin_quic(pkS, ms, scid, dcid) ) *
    get ( message(client, server, finished(label_finished, prf(ms, label_finished))) )
  }

  /////////////////////////////  FORMULA & EXEC /////////////////////////////
  val ok = bf( client_end_quic(pkS, kdf(dh(x_eph, exp(g, y_eph)), label_quic), scid, dcid) )
  val boot = not( bf(server_begin_quic(pkS, kdf(dh(y_eph, exp(g, x_eph)), label_quic), scid, dcid)) )
  val F: BHM_Formula = bHM { (boot * F) + ok }

  val Protocol = Agent { Client || Server }
  new BSC_Runner_BHM().execute(Protocol, F)
}
