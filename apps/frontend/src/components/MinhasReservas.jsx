import { useEffect, useState } from 'react'

const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')

export default function MinhasReservas({ token, onVoltar }) {
  const [reservas, setReservas] = useState([])
  const [erro, setErro] = useState('')
  const [carregando, setCarregando] = useState(true)

  async function carregar() {
    try {
      const response = await fetch(`${API_URL}/api/v1/reservas/minhas`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || 'Não foi possível carregar suas reservas.')
      setReservas(data)
      setErro('')
    } catch (error) {
      setErro(error.message)
    } finally {
      setCarregando(false)
    }
  }

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { carregar() }, [token])

  async function cancelar(id) {
    if (!window.confirm('Deseja cancelar esta solicitação de reserva?')) return
    try {
      const response = await fetch(`${API_URL}/api/v1/reservas/${id}/cancelar`, {
        method: 'PATCH',
        headers: { Authorization: `Bearer ${token}` },
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || 'Não foi possível cancelar a reserva.')
      setReservas(atual => atual.map(item => item.id === id ? data : item))
    } catch (error) {
      setErro(error.message)
    }
  }

  return (
    <main className="admin-page">
      <header className="admin-heading">
        <div><span className="details-label">SUA CONTA</span><h1>Minhas reservas</h1></div>
        <button type="button" className="details-back-button" onClick={onVoltar}>← Voltar ao site</button>
      </header>
      {erro && <p className="form-feedback" role="alert">{erro}</p>}
      {carregando ? <p>Carregando reservas...</p> : reservas.length ? (
        <div className="admin-reservations">
          {reservas.map(item => (
            <article key={item.id}>
              <strong>Reserva {item.id}</strong>
              <span>{item.data_checkin} até {item.data_checkout}</span>
              <span>{item.adultos} adulto(s), {item.criancas} criança(s)</span>
              <span>R$ {Number(item.valor_total).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</span>
              <span>Status: {item.status}</span>
              {item.status !== 'cancelada' && item.data_checkin > new Date().toISOString().slice(0, 10) && (
                <button type="button" onClick={() => cancelar(item.id)}>Cancelar</button>
              )}
            </article>
          ))}
        </div>
      ) : <p className="empty-message">Você ainda não possui reservas.</p>}
    </main>
  )
}
