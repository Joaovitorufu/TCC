using Microsoft.EntityFrameworkCore;
using backend_csharp.Models;

namespace backend_csharp.Data
{
    public class AppDbContext : DbContext
    {
        public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

        public DbSet<ForecastData> ForecastResults { get; set; }
    }
}
