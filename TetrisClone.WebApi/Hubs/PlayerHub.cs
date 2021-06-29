using Microsoft.AspNetCore.SignalR;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using TetrisClone.WebApi.Model;

namespace TetrisClone.WebApi.Hubs
{
    public class PlayerHub : Hub
    {
        public ConcurrentDictionary<string, List<string>> Games { get; set; }

        private const int PLAYERS_PER_GAME = 2;

        /*
            TODO: Fix assumption that there will only ever be two players connecting using same uniqueString
        */
        public async Task EnterGame(string gameId)
        {
            if (Games.Keys.Any(x => x == gameId))
                Games[gameId].Add(Context.ConnectionId);
            else
                Games[gameId] = new List<string> { Context.ConnectionId };

            if (Games[gameId].Count != PLAYERS_PER_GAME)
                await Clients
                    .Clients(Games[gameId])
                    .SendAsync("StartGame");

            await Clients
                .Clients(Games[gameId])
                .SendAsync("WaitForOpponent");
        }

        public async Task SendCurrentPiece(string gameId, Piece piece)
        {
            if (Games.Keys.All(x => x != gameId))
                return;

            await Clients
                .Clients(Games[gameId].First(x => x != Context.ConnectionId))
                .SendAsync("GetOpponentPiece");
        }
    }
}
