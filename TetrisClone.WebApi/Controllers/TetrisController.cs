using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace TetrisClone.WebApi.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class TetrisController : ControllerBase
    {
        private readonly ILogger<TetrisController> _logger;

        public TetrisController(ILogger<TetrisController> logger)
        {
            _logger = logger;
        }

        [HttpGet]
        public ActionResult Get()
        {
            return new EmptyResult();
        }
    }
}
