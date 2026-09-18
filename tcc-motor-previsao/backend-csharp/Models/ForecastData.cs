using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace backend_csharp.Models
{
    [Table("forecast_results")]
    public class ForecastData
    {
        [Key]
        [Column("id")]
        public int Id { get; set; }

        [Column("parameterization_name")]
        public string ParameterizationName { get; set; }

        [Column("rmse")]
        public double Rmse { get; set; }

        [Column("mae")]
        public double Mae { get; set; }

        [Column("forecast_data")]
        public string ForecastJson { get; set; }
    }
}
