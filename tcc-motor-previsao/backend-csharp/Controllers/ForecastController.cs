using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using backend_csharp.Data;
using System.Threading.Tasks;

namespace backend_csharp.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class ForecastController : ControllerBase
    {
        private readonly AppDbContext _context;

        public ForecastController(AppDbContext context)
        {
            _context = context;
        }

        [HttpGet]
        public async Task<IActionResult> GetForecasts()
        {
            var results = await _context.ForecastResults.ToListAsync();
            return Ok(results);
        }
    }
}
