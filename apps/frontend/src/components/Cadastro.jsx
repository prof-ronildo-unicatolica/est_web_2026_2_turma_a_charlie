import { useRef, useState } from 'react'

const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')

export default function Cadastro({ onVoltar, onCadastro }) {
  const [nome, setNome] = useState('')
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [confirmacao, setConfirmacao] = useState('')
  const [erro, setErro] = useState('')
  const [carregando, setCarregando] = useState(false)
  const envioEmAndamento = useRef(false)

  async function cadastrar(event) {
    event.preventDefault()
    if (envioEmAndamento.current) return
    if (senha.length < 8) {
      setErro('A senha deve ter pelo menos 8 caracteres.')
      return
    }
    if (senha !== confirmacao) {
      setErro('As senhas não coincidem.')
      return
    }
    envioEmAndamento.current = true
    setCarregando(true)
    setErro('')
    try {
      const response = await fetch(`${API_URL}/api/v1/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ nome: nome.trim(), email: email.trim(), senha }),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || 'Não foi possível criar a conta.')
      onCadastro(email.trim(), senha)
    } catch (error) {
      setErro(error.message)
    } finally {
      envioEmAndamento.current = false
      setCarregando(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-card" aria-busy={carregando}>
        <h1>Criar sua conta</h1>
        <form onSubmit={cadastrar}>
          <div className="login-field">
            <label htmlFor="cadastro-nome">Nome</label>
            <input id="cadastro-nome" value={nome} onChange={e => setNome(e.target.value)} maxLength={100} required />
          </div>
          <div className="login-field">
            <label htmlFor="cadastro-email">E-mail</label>
            <input id="cadastro-email" type="email" value={email} onChange={e => setEmail(e.target.value)} required />
          </div>
          <div className="login-field">
            <label htmlFor="cadastro-senha">Senha</label>
            <input id="cadastro-senha" type="password" value={senha} onChange={e => setSenha(e.target.value)} minLength={8} required />
          </div>
          <div className="login-field">
            <label htmlFor="cadastro-confirmacao">Confirmar senha</label>
            <input id="cadastro-confirmacao" type="password" value={confirmacao} onChange={e => setConfirmacao(e.target.value)} required />
          </div>
          {erro && <div className="login-error" role="alert">{erro}</div>}
          <button type="submit" className="login-submit" disabled={carregando}>
            {carregando ? 'Criando conta...' : 'Criar conta'}
          </button>
        </form>
        <button type="button" className="login-back" onClick={onVoltar}>Voltar para o login</button>
      </div>
    </div>
  )
}
