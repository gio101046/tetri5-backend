using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace TetrisClone.WebApi.Model
{
    public class Piece
    {
        public int X { get; set; }
        public int Y { get; set; }
        public PieceType Type { get; set; }
    }
}
