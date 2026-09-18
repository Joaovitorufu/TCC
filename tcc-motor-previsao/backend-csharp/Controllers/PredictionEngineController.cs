using Microsoft.AspNetCore.Mvc;
using System.Net.Http;
using System.Threading.Tasks;

namespace backend_csharp.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class PredictionEngineController : ControllerBase
    {
        private readonly IHttpClientFactory _httpClientFactory;

        public PredictionEngineController(IHttpClientFactory httpClientFactory)
        {
            _httpClientFactory = httpClientFactory;
        }

        [HttpPost("chamar-motor")]
        public async Task<IActionResult> RunPredictionEngine()
        {
            try
            {
                var client = _httpClientFactory.CreateClient();
                
                // A porta padrão do FastAPI/Uvicorn geralmente é 8000
                var pythonApiUrl = "http://localhost:8000/forecast/train";
                
                var response = await client.PostAsync(pythonApiUrl, null);

                if (response.IsSuccessStatusCode)
                {
                    // Retorna a resposta (as métricas e a mensagem de sucesso) vinda da API Python
                    var result = await response.Content.ReadAsStringAsync();
                    return Ok(result);
                }

                var errorMsg = await response.Content.ReadAsStringAsync();
                return StatusCode((int)response.StatusCode, $"Erro retornado pelo motor de previsão Python: {errorMsg}");
            }
            catch (HttpRequestException ex)
            {
                return StatusCode(500, $"Falha de conexão com o motor Python. Certifique-se de que ele está rodando na porta 8000. Erro: {ex.Message}");
            }
        }
    }
}
