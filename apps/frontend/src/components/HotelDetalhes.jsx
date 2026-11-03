export default function HotelDetalhes({ hotel, onVoltar }) {
  if (!hotel) {
    return null
  }

  const estrelas = hotel.categoria_estrelas || 0

  return (
    <div className="hotel-details-page">

      {/* VOLTAR */}
      <button
        className="details-back-button"
        onClick={onVoltar}
      >
        ← Voltar para os hotéis
      </button>

      {/* CAPA DO HOTEL */}
      <section className="hotel-details-cover">

        <img
          src={`https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1600&q=85`}
          alt={hotel.nome}
        />

        <div className="hotel-cover-overlay">
          <div className="hotel-cover-content">

            <div className="details-stars">
              {'★'.repeat(estrelas)}
              {'☆'.repeat(5 - estrelas)}
            </div>

            <h1>{hotel.nome}</h1>

            <p>
              📍 {hotel.cidade_nome}, {hotel.cidade_estado}
            </p>

          </div>
        </div>

      </section>

      {/* INFORMAÇÕES */}
      <section className="hotel-details-info">

        <div className="hotel-details-description">

          <span className="details-label">
            SOBRE O HOTEL
          </span>

          <h2>
            Uma estadia confortável para você
          </h2>

          <p>
            Encontre conforto e praticidade durante sua hospedagem.
            Escolha o quarto que melhor atende às suas necessidades
            e aproveite sua estadia.
          </p>

        </div>

        <div className="hotel-details-rating">

          <div className="rating-number">
            {estrelas}
          </div>

          <div>
            <strong>
              Classificação
            </strong>

            <span>
              Hotel {estrelas} estrelas
            </span>
          </div>

        </div>

      </section>

      {/* QUARTOS */}
      <section className="rooms-section">

        <div className="rooms-heading">

          <div>
            <span className="details-label">
              ACOMODAÇÕES
            </span>

            <h2>
              Quartos disponíveis
            </h2>
          </div>

          <span className="rooms-count">
            {hotel.quartos?.length || 0} quarto
            {hotel.quartos?.length !== 1 ? 's' : ''}
          </span>

        </div>

        {hotel.quartos && hotel.quartos.length > 0 ? (

          <div className="rooms-grid">

            {hotel.quartos.map((quarto) => (

              <article
                className="room-card"
                key={quarto.quarto_id}
              >

                <div className="room-image">
                  <img
                    src="https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=800&q=80"
                    alt={quarto.tipo}
                  />
                </div>

                <div className="room-card-content">

                  <span className="room-type">
                    ACOMODAÇÃO
                  </span>

                  <h3>
                    {quarto.tipo}
                  </h3>

                  <div className="room-price">

                    <strong>
                      R$ {Number(quarto.preco_diaria).toLocaleString(
                        'pt-BR',
                        {
                          minimumFractionDigits: 2,
                        }
                      )}
                    </strong>

                    <span>
                      / noite
                    </span>

                  </div>

                  <div className="room-divider"></div>

                  <div className="room-capacity">

                    <div>
                      <span className="capacity-icon">
                        👤
                      </span>

                      <div>
                        <small>
                          Adultos
                        </small>

                        <strong>
                          Até {quarto.max_adultos}
                        </strong>
                      </div>
                    </div>

                    <div>
                      <span className="capacity-icon">
                        👶
                      </span>

                      <div>
                        <small>
                          Crianças
                        </small>

                        <strong>
                          Até {quarto.max_criancas}
                        </strong>
                      </div>
                    </div>

                  </div>

                  <button className="reserve-button">
                    Reservar quarto
                  </button>

                </div>

              </article>

            ))}

          </div>

        ) : (

          <div className="empty-message">
            Nenhum quarto disponível para este hotel.
          </div>

        )}

      </section>

    </div>
  )
}