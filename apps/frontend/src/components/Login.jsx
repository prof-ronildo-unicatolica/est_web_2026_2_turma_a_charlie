import { useState } from 'react'

const API_URL = 'http://localhost:8000'

export default function Login({ onVoltar, onLogin }) {
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [erro, setErro] = useState('')
  const [carregando, setCarregando] = useState(false)

  async function fazerLogin(event) {
    event.preventDefault()

    setErro('')
    setCarregando(true)

    try {
      const response = await fetch(`${API_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify({
          email: email,
          senha: senha,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'E-mail ou senha incorretos.')
      }

    // O backend básico retorna o e-mail como access_token.
    localStorage.setItem('access_token', data.access_token)

     // Atualiza o App e volta para a Home.
    onLogin(data.access_token)

    } catch (error) {
      console.error(error)
      setErro(error.message)
    } finally {
      setCarregando(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">

        <h1>Bem-vindo de volta</h1>

        <form onSubmit={fazerLogin}>

          <div className="login-field">
            <label htmlFor="email">E-mail</label>

            <input
              id="email"
              type="email"
              placeholder="Digite seu e-mail"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </div>

          <div className="login-field">
            <label htmlFor="senha">Senha</label>

            <input
              id="senha"
              type="password"
              placeholder="Digite sua senha"
              value={senha}
              onChange={(event) => setSenha(event.target.value)}
              required
            />
          </div>

          {erro && (
            <div className="login-error">
              {erro}
            </div>
          )}

          <button
            type="submit"
            className="login-submit"
            disabled={carregando}
          >
            {carregando ? 'Entrando...' : 'Entrar'}
          </button>

        </form>

        <button
          type="button"
          className="login-back"
          onClick={onVoltar}
        >
          Voltar para a página inicial
        </button>

      </div>
    </div>
  )
}
