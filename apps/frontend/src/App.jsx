import { useEffect, useRef, useState } from 'react'
import './custom.css'
import Login from './components/Login'
import HotelDetalhes from './components/HotelDetalhes'

const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')

function App() {
  const [tela, setTela] = useState('home')
  const [usuarioLogado, setUsuarioLogado] = useState(
  localStorage.getItem('access_token')
)
  const [hotelSelecionado, setHotelSelecionado] = useState(null)
  const [hoteis, setHoteis] = useState([])
  const [loading, setLoading] = useState(true)
  const [erro, setErro] = useState(null)
  const [favoritos, setFavoritos] = useState(() => {
    try {
      const salvos = JSON.parse(localStorage.getItem('hotel_favoritos') || '[]')
      return Array.isArray(salvos) ? salvos : []
    } catch {
      return []
    }
  })
  const requisicaoEmAndamento = useRef(false)

  const [cidade, setCidade] = useState('')
  const [estrelas, setEstrelas] = useState('')
  const [checkin, setCheckin] = useState('')
  const [checkout, setCheckout] = useState('')
  const [adultos, setAdultos] = useState(2)
  const [criancas, setCriancas] = useState(0)

  useEffect(() => {
    carregarHoteis()
  }, [])

  useEffect(() => {
    localStorage.setItem('hotel_favoritos', JSON.stringify(favoritos))
  }, [favoritos])

  function alternarFavorito(hotelId) {
    setFavoritos((atuais) =>
      atuais.includes(hotelId)
        ? atuais.filter((id) => id !== hotelId)
        : [...atuais, hotelId]
    )
  }

  async function carregarHoteis() {
    if (requisicaoEmAndamento.current) return
    requisicaoEmAndamento.current = true
    try {
      setLoading(true)

      const response = await fetch(`${API_URL}/api/v1/busca/hoteis`)

      if (!response.ok) {
        throw new Error('Não foi possível carregar os hotéis.')
      }

      const data = await response.json()

      setHoteis(data)
      setErro(null)
    } catch (error) {
      console.error(error)
      setErro('Não foi possível carregar os hotéis.')
    } finally {
      setLoading(false)
      requisicaoEmAndamento.current = false
    }
  }

  async function pesquisar() {
    if (requisicaoEmAndamento.current) return
    requisicaoEmAndamento.current = true
    try {
      setLoading(true)

      const params = new URLSearchParams()

      if (cidade.trim()) {
        params.append('cidade_id', cidade.trim())
      }

      if (estrelas) {
        params.append('estrelas', estrelas)
      }

      const url = `${API_URL}/api/v1/busca/hoteis${
        params.toString() ? `?${params.toString()}` : ''
      }`

      const response = await fetch(url)

      if (!response.ok) {
        throw new Error('Erro ao realizar busca.')
      }

      const data = await response.json()

      setHoteis(data)
      setErro(null)
    } catch (error) {
      console.error(error)
      setErro('Não foi possível realizar a busca.')
    } finally {
      setLoading(false)
      requisicaoEmAndamento.current = false
    }
  }

  if (tela === 'login') {
  return (
    <Login
      onVoltar={() => setTela('home')}
      onLogin={() => {
        setUsuarioLogado(true)
        setTela('home')
      }}
    />
  )
}

  if (tela === 'detalhes' && hotelSelecionado) {
    return (
      <HotelDetalhes
        hotel={hotelSelecionado}
        onVoltar={() => setTela('home')}
      />
    )
  }

  function menorPreco(hotel) {
    if (!hotel.quartos || hotel.quartos.length === 0) {
      return null
    }

    return Math.min(
      ...hotel.quartos.map((quarto) => Number(quarto.preco_diaria))
    )
  }

  return (
    <div className="hotel-app">

      {/* HEADER */}
      <header className="hotel-header">
        <div className="hotel-logo">

          <span className="logo-icon">✧</span>
          <span>BEM-VINDO</span>

        </div>


        <nav className="hotel-nav">
          <a href="#inicio">◉ <span>Explorar</span></a>
          <a href="#hoteis">▣ <span>Hotéis</span></a>
          <a href="#favoritos">♡ <span>Favoritos ({favoritos.length})</span></a>
        </nav>

        <div className="user-area">
        <div className="user-icon">👤</div>

        {usuarioLogado ? (
          <>
            <span>Olá, usuário</span>

            <button type="button"
              className="login-button"
              onClick={() => {
                localStorage.removeItem('access_token')
                setUsuarioLogado(null)
              }}
            >
              Sair
            </button>
          </>
        ) : (
          <>
            <span>Olá, usuário</span>

            <button type="button"
              className="login-button"
              onClick={() => setTela('login')}
            >
              Fazer login
            </button>
          </>
        )}
      </div>
      </header>

      {/* HERO */}
      <main id="inicio">

        <section className="hero">


            <div className="hero-content">
              <div className="hero-text">
                <h1>
                  Encontre sua
                  <br />
                  próxima estadia
                </h1>

                <p>
                  Pesquise hotéis, datas e experiências inesquecíveis
                </p>
              </div>
            </div>


          {/* SEARCH BOX */}
          <div className="search-box">

            <div className="search-field destination">
              <span className="field-icon">●</span>

              <div>
                <label>Para onde?</label>

                <input
                  type="text"
                  placeholder="ID da cidade"
                  value={cidade}
                  onChange={(e) => setCidade(e.target.value)}
                />
              </div>
            </div>

            <div className="search-field">
              <span className="field-icon">▣</span>

              <div>
                <label>Check-in</label>

                <input
                  type="date"
                  value={checkin}
                  onChange={(e) => setCheckin(e.target.value)}
                />
              </div>
            </div>

            <div className="search-field">
              <span className="field-icon">▣</span>

              <div>
                <label>Check-out</label>

                <input
                  type="date"
                  value={checkout}
                  onChange={(e) => setCheckout(e.target.value)}
                />
              </div>
            </div>

            <div className="search-field guests">
              <span className="field-icon">♙</span>

              <div>
                <label>Hóspedes</label>

                <div className="guest-controls">
                  <select
                    value={adultos}
                    onChange={(e) => setAdultos(Number(e.target.value))}
                  >
                    {[1, 2, 3, 4, 5, 6].map((numero) => (
                      <option key={numero} value={numero}>
                        {numero} adulto{numero > 1 ? 's' : ''}
                      </option>
                    ))}
                  </select>

                  <select
                    value={criancas}
                    onChange={(e) => setCriancas(Number(e.target.value))}
                  >
                    {[0, 1, 2, 3, 4].map((numero) => (
                      <option key={numero} value={numero}>
                        {numero} criança{numero !== 1 ? 's' : ''}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            <div className="search-field stars">
              <div>
                <label>Estrelas</label>

                <select
                  value={estrelas}
                  onChange={(e) => setEstrelas(e.target.value)}
                >
                  <option value="">Todas</option>
                  <option value="3">3 estrelas</option>
                  <option value="4">4 estrelas</option>
                  <option value="5">5 estrelas</option>
                </select>
              </div>
            </div>

            <button
              type="button"
              className="search-button"
              onClick={pesquisar}
              disabled={loading}
              aria-busy={loading}
            >
              {loading ? 'Buscando...' : 'Pesquisar'}
            </button>

          </div>
        </section>

        {/* HOTELS */}
        <section className="hotel-section" id="hoteis">

          <div className="section-heading">
            <h2>Sugestões para você</h2>

            <button type="button" onClick={carregarHoteis} disabled={loading}>
              {loading ? 'Carregando...' : 'Ver todas →'}
            </button>
          </div>

          {erro && (
            <div className="error-message">
              {erro}
            </div>
          )}

          {loading ? (
            <div className="hotel-grid">

              {[1, 2, 3].map((item) => (
                <div className="hotel-card skeleton-card" key={item}>
                  <div className="skeleton image-skeleton"></div>

                  <div className="hotel-info">
                    <div className="skeleton line-skeleton"></div>
                    <div className="skeleton small-skeleton"></div>
                    <div className="skeleton small-skeleton"></div>
                  </div>
                </div>
              ))}

            </div>
          ) : (
            <div className="hotel-grid">

              {hoteis.map((hotel) => {

                const preco = menorPreco(hotel)

                const favorito = favoritos.includes(hotel.hotel_id)

                return (
                  <article className="hotel-card" key={hotel.hotel_id}>
                    <div className="hotel-image">

                      <img
                        src={`https://images.unsplash.com/photo-${
                          [
                            '1566073771259-6a8506099945',
                            '1582719478250-c89cae4dc85b',
                            '1564501049412-61c2a3083791',
                          ][Math.abs(
                            hotel.hotel_id
                              .split('')
                              .reduce(
                                (total, letra) =>
                                  total + letra.charCodeAt(0),
                                0
                              )
                          ) % 3]
                        }?auto=format&fit=crop&w=700&q=80`}
                        alt={hotel.nome}
                      />

                      <button
                        type="button"
                        className="favorite-button"
                        aria-label={favorito ? 'Remover dos favoritos' : 'Adicionar aos favoritos'}
                        aria-pressed={favorito}
                        onClick={() => alternarFavorito(hotel.hotel_id)}
                      >
                        {favorito ? '♥' : '♡'}
                      </button>
                    </div>

                    <div className="hotel-info">

                      <h3>{hotel.nome}</h3>

                      <p className="hotel-location">
                        <span>●</span>
                        {hotel.cidade_nome}, {hotel.cidade_estado}
                      </p>

                      <div className="hotel-bottom">

                        <div>
                          <div className="stars-display">
                            {'★'.repeat(hotel.categoria_estrelas)}
                            <span>
                              {'☆'.repeat(
                                5 - hotel.categoria_estrelas
                              )}
                            </span>
                          </div>

                          <small>
                            {hotel.categoria_estrelas} estrelas
                          </small>
                        </div>

                        <div className="price">

                          {preco ? (
                            <>
                              <strong>
                                R$ {preco.toLocaleString('pt-BR', {
                                  minimumFractionDigits: 2,
                                })}
                              </strong>

                              <small>
                                por noite
                              </small>
                            </>
                          ) : (
                            <small>
                              Consulte disponibilidade
                            </small>
                          )}

                        </div>

                      </div>

                    </div>

                    <button
                      type="button"
                      className="hotel-open-button"
                      onClick={() => {
                        setHotelSelecionado(hotel)
                        setTela('detalhes')
                      }}
                    >
                      Ver detalhes
                    </button>
                  </article>
                )
              })}

            </div>
          )}

          {!loading && hoteis.length === 0 && (
            <div className="empty-message">
              Nenhum hotel encontrado para os filtros selecionados.
            </div>
          )}

        </section>

        <section className="favorites-section" id="favoritos" aria-labelledby="favorites-title">
          <div className="section-heading">
            <h2 id="favorites-title">Seus favoritos</h2>
          </div>
          {favoritos.length === 0 ? (
            <p className="empty-message">Você ainda não adicionou hotéis aos favoritos.</p>
          ) : (
            <ul className="favorites-list">
              {hoteis.filter((hotel) => favoritos.includes(hotel.hotel_id)).map((hotel) => (
                <li key={hotel.hotel_id}>
                  <button type="button" onClick={() => {
                    setHotelSelecionado(hotel)
                    setTela('detalhes')
                  }}>
                    {hotel.nome} — {hotel.cidade_nome}, {hotel.cidade_estado}
                  </button>
                  <button type="button" onClick={() => alternarFavorito(hotel.hotel_id)}>
                    Remover
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* AVALIAÇÕES */}
        <section className="reviews-section">
          <div className="reviews-header">
            <div className="reviews-icon">
              💬
            </div>

            <div>
              <h2>Avaliações de hóspedes</h2>
              <p>
                As experiências reais dos nossos hóspedes aparecerão aqui.
              </p>
            </div>
          </div>

          <div className="empty-reviews">
            <div className="empty-reviews-icon">
              ☆
            </div>

            <h3>Ainda não há avaliações</h3>

            <p>
              Seja o primeiro a avaliar uma hospedagem após sua estadia.
            </p>
          </div>
        </section>

      </main>
    </div>
  )
}

export default App
