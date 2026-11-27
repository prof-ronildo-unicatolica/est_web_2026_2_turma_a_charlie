import { useEffect, useState } from 'react'

const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')

export default function HotelDetalhes({ hotel, onVoltar, token }) {
  const [checkin, setCheckin] = useState('')
  const [checkout, setCheckout] = useState('')
  const [adultos, setAdultos] = useState(2)
  const [criancas, setCriancas] = useState(0)
  const [mensagemReserva, setMensagemReserva] = useState('')
  const [carregandoReserva, setCarregandoReserva] = useState(false)
  const [avaliacoes, setAvaliacoes] = useState([])
  const [nota, setNota] = useState(5)
  const [comentario, setComentario] = useState('')
  const [mensagemAvaliacao, setMensagemAvaliacao] = useState('')
  const [carregandoAvaliacao, setCarregandoAvaliacao] = useState(false)

  useEffect(() => {
    let ativo = true
    fetch(`${API_URL}/api/v1/hoteis/${hotel.hotel_id}/avaliacoes`)
      .then(response => response.ok ? response.json() : Promise.reject(new Error('Falha ao carregar avaliações')))
      .then(data => { if (ativo) setAvaliacoes(data) })
      .catch(() => { if (ativo) setAvaliacoes([]) })
    return () => { ativo = false }
  }, [hotel.hotel_id])

  async function reservar(quarto) {
    setMensagemReserva('')
    if (!token) {
      setMensagemReserva('Faça login para reservar um quarto.')
      return
    }
    if (!checkin || !checkout || checkout <= checkin) {
      setMensagemReserva('Informe datas válidas. O check-out deve ser posterior ao check-in.')
      return
    }
    setCarregandoReserva(true)
    try {
      const response = await fetch(`${API_URL}/api/v1/reservas`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          quarto_id: quarto.quarto_id,
          data_checkin: checkin,
          data_checkout: checkout,
          adultos,
          criancas,
        }),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || 'Não foi possível criar a reserva.')
      setMensagemReserva(`Solicitação criada! Código: ${data.id}. Valor: R$ ${Number(data.valor_total).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}. Status: ${data.status}.`)
    } catch (error) {
      setMensagemReserva(error.message)
    } finally {
      setCarregandoReserva(false)
    }
  }

  async function enviarAvaliacao(event) {
    event.preventDefault()
    setMensagemAvaliacao('')
    if (!token) {
      setMensagemAvaliacao('Faça login para avaliar este hotel.')
      return
    }
    setCarregandoAvaliacao(true)
    try {
      const response = await fetch(`${API_URL}/api/v1/avaliacoes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ hotel_id: hotel.hotel_id, nota: Number(nota), comentario }),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || 'Não foi possível enviar a avaliação.')
      setAvaliacoes(atual => [data, ...atual])
      setComentario('')
      setMensagemAvaliacao('Avaliação publicada com sucesso.')
    } catch (error) {
      setMensagemAvaliacao(error.message)
    } finally {
      setCarregandoAvaliacao(false)
    }
  }

  if (!hotel) return null
  const estrelas = hotel.categoria_estrelas || 0

  return (
    <div className="hotel-details-page">
      <button type="button" className="details-back-button" onClick={onVoltar}>← Voltar para os hotéis</button>
      <section className="hotel-details-cover">
        <img src="https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1600&q=85" alt={hotel.nome} />
        <div className="hotel-cover-overlay">
          <div className="hotel-cover-content">
            <div className="details-stars">{'★'.repeat(estrelas)}{'☆'.repeat(5 - estrelas)}</div>
            <h1>{hotel.nome}</h1>
            <p>📍 {hotel.cidade_nome}, {hotel.cidade_estado}</p>
          </div>
        </div>
      </section>

      <section className="hotel-details-info">
        <div className="hotel-details-description">
          <span className="details-label">SOBRE O HOTEL</span>
          <h2>Uma estadia confortável para você</h2>
          <p>Encontre conforto e praticidade durante sua hospedagem. Escolha o quarto que melhor atende às suas necessidades e aproveite sua estadia.</p>
        </div>
        <div className="hotel-details-rating">
          <div className="rating-number">{estrelas}</div>
          <div><strong>Classificação</strong><span>Hotel {estrelas} estrelas</span></div>
        </div>
      </section>

      <section className="rooms-section">
        <div className="rooms-heading">
          <div><span className="details-label">ACOMODAÇÕES</span><h2>Quartos disponíveis</h2></div>
          <span className="rooms-count">{hotel.quartos?.length || 0} quarto(s)</span>
        </div>

        <div className="booking-controls">
          <label>Check-in<input type="date" min={new Date().toISOString().slice(0, 10)} value={checkin} onChange={e => setCheckin(e.target.value)} /></label>
          <label>Check-out<input type="date" min={checkin || new Date().toISOString().slice(0, 10)} value={checkout} onChange={e => setCheckout(e.target.value)} /></label>
          <label>Adultos<select value={adultos} onChange={e => setAdultos(Number(e.target.value))}>{[1,2,3,4,5,6].map(n => <option key={n} value={n}>{n}</option>)}</select></label>
          <label>Crianças<select value={criancas} onChange={e => setCriancas(Number(e.target.value))}>{[0,1,2,3,4].map(n => <option key={n} value={n}>{n}</option>)}</select></label>
        </div>
        {mensagemReserva && <p className="form-feedback" role="status">{mensagemReserva}</p>}

        {hotel.quartos?.length ? (
          <div className="rooms-grid">
            {hotel.quartos.map(quarto => (
              <article className="room-card" key={quarto.quarto_id}>
                <div className="room-image"><img src="https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=800&q=80" alt={quarto.tipo} /></div>
                <div className="room-card-content">
                  <span className="room-type">ACOMODAÇÃO</span>
                  <h3>{quarto.tipo}</h3>
                  <div className="room-price"><strong>R$ {Number(quarto.preco_diaria).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</strong><span>/ noite</span></div>
                  <div className="room-divider" />
                  <div className="room-capacity">
                    <div><span className="capacity-icon">👤</span><div><small>Adultos</small><strong>Até {quarto.max_adultos}</strong></div></div>
                    <div><span className="capacity-icon">👶</span><div><small>Crianças</small><strong>Até {quarto.max_criancas}</strong></div></div>
                  </div>
                  <button type="button" className="reserve-button" onClick={() => reservar(quarto)} disabled={carregandoReserva}>
                    {carregandoReserva ? 'Enviando...' : 'Solicitar reserva'}
                  </button>
                </div>
              </article>
            ))}
          </div>
        ) : <div className="empty-message">Nenhum quarto cadastrado para este hotel.</div>}
      </section>

      <section className="reviews-section">
        <div className="reviews-header"><div className="reviews-icon">💬</div><div><h2>Avaliações de hóspedes</h2><p>Opiniões de hóspedes que concluíram sua estadia.</p></div></div>
        {token && (
          <form className="review-form" onSubmit={enviarAvaliacao}>
            <label>Nota<select value={nota} onChange={e => setNota(e.target.value)}>{[5,4,3,2,1].map(n => <option key={n} value={n}>{n} estrela(s)</option>)}</select></label>
            <label>Comentário<textarea value={comentario} onChange={e => setComentario(e.target.value)} minLength={3} maxLength={2000} required /></label>
            <button type="submit" className="reserve-button" disabled={carregandoAvaliacao}>{carregandoAvaliacao ? 'Enviando...' : 'Publicar avaliação'}</button>
          </form>
        )}
        {mensagemAvaliacao && <p className="form-feedback" role="status">{mensagemAvaliacao}</p>}
        {avaliacoes.length ? (
          <div className="review-list">{avaliacoes.map(item => <article className="review-item" key={item.id}><strong>{'★'.repeat(item.nota)}{'☆'.repeat(5-item.nota)}</strong><p>{item.comentario}</p><small>{new Date(item.criada_em).toLocaleDateString('pt-BR')}</small></article>)}</div>
        ) : <p className="empty-message">Ainda não há avaliações publicadas.</p>}
      </section>
    </div>
  )
}
