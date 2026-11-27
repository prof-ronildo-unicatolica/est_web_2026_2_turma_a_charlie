import { useEffect, useState } from 'react'

const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')

export default function AdminPanel({ token, onVoltar }) {
  const [cidades, setCidades] = useState([])
  const [hoteis, setHoteis] = useState([])
  const [quartos, setQuartos] = useState([])
  const [comodidades, setComodidades] = useState([])
  const [reservas, setReservas] = useState([])
  const [mensagem, setMensagem] = useState('')
  const [cidade, setCidade] = useState({ nome: '', estado: 'CE' })
  const [hotel, setHotel] = useState({ nome: '', cidade_id: '', categoria_estrelas: 3 })
  const [quarto, setQuarto] = useState({ hotel_id: '', tipo: '', preco_diaria: '', max_adultos: 2, max_criancas: 0 })
  const [comodidade, setComodidade] = useState('')

  async function requisitar(path, options = {}) {
    const response = await fetch(`${API_URL}/api/v1${path}`, {
      ...options,
      headers: {
        Accept: 'application/json',
        ...(options.body ? { 'Content-Type': 'application/json' } : {}),
        Authorization: `Bearer ${token}`,
        ...options.headers,
      },
    })
    const data = response.status === 204 ? null : await response.json()
    if (!response.ok) throw new Error(data?.detail || 'Não foi possível concluir a operação.')
    return data
  }

  async function carregar() {
    try {
      const [c, h, q, m, r] = await Promise.all([
        requisitar('/cidades'), requisitar('/hoteis'), requisitar('/quartos'),
        requisitar('/comodidades'), requisitar('/reservas/admin/todas'),
      ])
      setCidades(c); setHoteis(h); setQuartos(q); setComodidades(m); setReservas(r)
      if (!hotel.cidade_id && c.length) setHotel(atual => ({ ...atual, cidade_id: c[0].id }))
      if (!quarto.hotel_id && h.length) setQuarto(atual => ({ ...atual, hotel_id: h[0].id }))
      setMensagem('')
    } catch (error) { setMensagem(error.message) }
  }

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { carregar() }, [])

  async function enviar(path, body, limpar) {
    try {
      await requisitar(path, { method: 'POST', body: JSON.stringify(body) })
      limpar()
      await carregar()
      setMensagem('Operação concluída com sucesso.')
    } catch (error) { setMensagem(error.message) }
  }

  async function confirmar(id) {
    try {
      await requisitar(`/reservas/${id}/confirmar`, { method: 'PATCH' })
      await carregar()
      setMensagem('Reserva confirmada.')
    } catch (error) { setMensagem(error.message) }
  }

  async function editarCidade(item) {
    const nome = window.prompt('Nome da cidade:', item.nome)
    if (nome === null) return
    const estado = window.prompt('UF:', item.estado)
    if (estado === null) return
    try {
      await requisitar(`/cidades/${item.id}`, { method: 'PATCH', body: JSON.stringify({ nome, estado }) })
      await carregar()
      setMensagem('Cidade atualizada.')
    } catch (error) { setMensagem(error.message) }
  }

  async function excluirCidade(id) {
    if (!window.confirm('Excluir esta cidade? Só é permitido quando não há hotéis vinculados.')) return
    try {
      await requisitar(`/cidades/${id}`, { method: 'DELETE' })
      await carregar()
      setMensagem('Cidade excluída.')
    } catch (error) { setMensagem(error.message) }
  }

  async function editarHotel(item) {
    const nome = window.prompt('Nome do hotel:', item.nome)
    if (nome === null) return
    const estrelas = window.prompt('Classificação (1 a 5):', '3')
    if (estrelas === null) return
    const categoria_estrelas = Number(estrelas)
    if (!Number.isInteger(categoria_estrelas) || categoria_estrelas < 1 || categoria_estrelas > 5) {
      setMensagem('A classificação deve ser um número entre 1 e 5.')
      return
    }
    try {
      await requisitar(`/hoteis/${item.id}`, { method: 'PATCH', body: JSON.stringify({ nome, categoria_estrelas }) })
      await carregar()
      setMensagem('Hotel atualizado.')
    } catch (error) { setMensagem(error.message) }
  }

  async function excluirHotel(id) {
    if (!window.confirm('Excluir este hotel? A operação é bloqueada se houver reservas vinculadas.')) return
    try {
      await requisitar(`/hoteis/${id}`, { method: 'DELETE' })
      await carregar()
      setMensagem('Hotel excluído.')
    } catch (error) { setMensagem(error.message) }
  }

  async function excluirQuarto(id) {
    if (!window.confirm('Deseja realmente excluir este quarto?')) return
    try {
      await requisitar(`/quartos/${id}`, { method: 'DELETE' })
      await carregar()
      setMensagem('Quarto excluído.')
    } catch (error) { setMensagem(error.message) }
  }

  async function excluirComodidade(id) {
    if (!window.confirm('Deseja realmente excluir esta comodidade?')) return
    try {
      await requisitar(`/comodidades/${id}`, { method: 'DELETE' })
      await carregar()
      setMensagem('Comodidade excluída.')
    } catch (error) { setMensagem(error.message) }
  }

  return (
    <main className="admin-page">
      <header className="admin-heading">
        <div><span className="details-label">GERENCIAMENTO</span><h1>Painel administrativo</h1></div>
        <button type="button" className="details-back-button" onClick={onVoltar}>← Voltar ao site</button>
      </header>
      {mensagem && <p className="form-feedback" role="status">{mensagem}</p>}

      <section className="admin-section">
        <h2>Cidades</h2>
        <form className="admin-form" onSubmit={e => { e.preventDefault(); enviar('/cidades', cidade, () => setCidade({ nome: '', estado: 'CE' })) }}>
          <label>Nome<input required value={cidade.nome} onChange={e => setCidade({ ...cidade, nome: e.target.value })} /></label>
          <label>UF<input required minLength={2} maxLength={2} value={cidade.estado} onChange={e => setCidade({ ...cidade, estado: e.target.value.toUpperCase() })} /></label>
          <button type="submit">Cadastrar cidade</button>
        </form>
        <ul>{cidades.map(item => <li key={item.id}>{item.nome} - {item.estado} <button type="button" onClick={() => editarCidade(item)}>Editar</button> <button type="button" onClick={() => excluirCidade(item.id)}>Excluir</button></li>)}</ul>
      </section>

      <section className="admin-section">
        <h2>Hotéis</h2>
        <form className="admin-form" onSubmit={e => { e.preventDefault(); enviar('/hoteis', { ...hotel, categoria_estrelas: Number(hotel.categoria_estrelas), comodidade_ids: [] }, () => setHotel({ ...hotel, nome: '' })) }}>
          <label>Nome<input required value={hotel.nome} onChange={e => setHotel({ ...hotel, nome: e.target.value })} /></label>
          <label>Cidade<select required value={hotel.cidade_id} onChange={e => setHotel({ ...hotel, cidade_id: e.target.value })}>{cidades.map(item => <option key={item.id} value={item.id}>{item.nome} - {item.estado}</option>)}</select></label>
          <label>Estrelas<select value={hotel.categoria_estrelas} onChange={e => setHotel({ ...hotel, categoria_estrelas: e.target.value })}>{[1,2,3,4,5].map(n => <option key={n}>{n}</option>)}</select></label>
          <button type="submit" disabled={!cidades.length}>Cadastrar hotel</button>
        </form>
        <ul>{hoteis.map(item => <li key={item.id}>{item.nome} <button type="button" onClick={() => editarHotel(item)}>Editar</button> <button type="button" onClick={() => excluirHotel(item.id)}>Excluir</button></li>)}</ul>
      </section>

      <section className="admin-section">
        <h2>Quartos</h2>
        <form className="admin-form" onSubmit={e => { e.preventDefault(); enviar('/quartos', { ...quarto, preco_diaria: Number(quarto.preco_diaria), max_adultos: Number(quarto.max_adultos), max_criancas: Number(quarto.max_criancas) }, () => setQuarto(atual => ({ ...atual, tipo: '', preco_diaria: '' }))) }}>
          <label>Hotel<select required value={quarto.hotel_id} onChange={e => setQuarto({ ...quarto, hotel_id: e.target.value })}>{hoteis.map(item => <option key={item.id} value={item.id}>{item.nome}</option>)}</select></label>
          <label>Tipo<input required value={quarto.tipo} onChange={e => setQuarto({ ...quarto, tipo: e.target.value })} /></label>
          <label>Diária (R$)<input required type="number" min="0.01" step="0.01" value={quarto.preco_diaria} onChange={e => setQuarto({ ...quarto, preco_diaria: e.target.value })} /></label>
          <label>Adultos<input required type="number" min="1" value={quarto.max_adultos} onChange={e => setQuarto({ ...quarto, max_adultos: e.target.value })} /></label>
          <label>Crianças<input required type="number" min="0" value={quarto.max_criancas} onChange={e => setQuarto({ ...quarto, max_criancas: e.target.value })} /></label>
          <button type="submit" disabled={!hoteis.length}>Cadastrar quarto</button>
        </form>
        <ul>{quartos.map(item => <li key={item.id}>{item.tipo} — R$ {Number(item.preco_diaria).toFixed(2)} <button type="button" onClick={() => excluirQuarto(item.id)}>Excluir</button></li>)}</ul>
      </section>

      <section className="admin-section">
        <h2>Comodidades</h2>
        <form className="admin-form" onSubmit={e => { e.preventDefault(); enviar('/comodidades', { nome: comodidade }, () => setComodidade('')) }}>
          <label>Nome<input required value={comodidade} onChange={e => setComodidade(e.target.value)} /></label>
          <button type="submit">Cadastrar comodidade</button>
        </form>
        <ul>{comodidades.map(item => <li key={item.id}>{item.nome} <button type="button" onClick={() => excluirComodidade(item.id)}>Excluir</button></li>)}</ul>
      </section>

      <section className="admin-section">
        <h2>Reservas</h2>
        {reservas.length ? <div className="admin-reservations">{reservas.map(item => <article key={item.id}>
          <strong>{item.id}</strong><span>{item.data_checkin} até {item.data_checkout}</span>
          <span>{item.adultos} adulto(s), {item.criancas} criança(s)</span>
          <span>R$ {Number(item.valor_total).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</span>
          <span>Status: {item.status}</span>
          {item.status === 'pendente' && <button type="button" onClick={() => confirmar(item.id)}>Confirmar</button>}
        </article>)}</div> : <p>Nenhuma reserva cadastrada.</p>}
      </section>
      <button type="button" onClick={carregar}>Atualizar dados</button>
    </main>
  )
}
