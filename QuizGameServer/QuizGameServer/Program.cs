using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace QuizGameServer
{
    class Program
    {
        static void Main(string[] args)
        {
            var server = new QuizServer();
            server.Start();
        }
    }

    public class QuizServer
    {
        private TcpListener listener;
        private List<ClientHandler> clients = new List<ClientHandler>();
        private List<Question> questions = new List<Question>();
        private int currentQuestion = 0;
        private Dictionary<string, int> scores = new Dictionary<string, int>();
        private bool gameInProgress = false;
        private const int ANSWER_TIME = 15; // seconds

        public QuizServer()
        {
            InitializeQuestions();
        }

        private void InitializeQuestions()
        {
            questions.Add(new Question("What is the capital of France?",
                new[] { "London", "Berlin", "Paris", "Madrid" }, 2));
            questions.Add(new Question("What is 36 / 6?",
                new[] { "3", "9", "12", "6" }, 3));
            questions.Add(new Question("Which planet is known as the Red Planet?",
                new[] { "Venus", "Mars", "Jupiter", "Saturn" }, 1));
            questions.Add(new Question("Who wrote 'Romeo and Juliet'?",
                new[] { "Dickens", "Shakespeare", "Hemingway", "Austen" }, 1));
            questions.Add(new Question("What is the largest ocean?",
                new[] { "Atlantic", "Indian", "Arctic", "Pacific" }, 3));
        }

        public void Start()
        {
            try
            {
                listener = new TcpListener(IPAddress.Any, 5001);
                listener.Server.SetSocketOption(SocketOptionLevel.Socket, SocketOptionName.ReuseAddress, true);
                listener.Start();
                Console.WriteLine("Quiz Server started on port 5001");
                Console.WriteLine("Waiting for players to connect...");
                Console.WriteLine("Type 'start' to begin the game when ready");
                Console.WriteLine("Type 'quit' to stop the server\n");

                Task.Run(() => AcceptClients());
                ProcessCommands();
            }
            catch (SocketException ex)
            {
                Console.WriteLine($"Error starting server: {ex.Message}");
                Console.WriteLine("Port 5000 may already be in use. Close any other instances and try again.");
                Console.WriteLine("Press any key to exit...");
                Console.ReadKey();
            }
        }

        private async Task AcceptClients()
        {
            while (true)
            {
                try
                {
                    var client = await listener.AcceptTcpClientAsync();
                    var handler = new ClientHandler(client, this);
                    clients.Add(handler);
                    _ = handler.HandleClient();
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error accepting client: {ex.Message}");
                }
            }
        }

        private void ProcessCommands()
        {
            while (true)
            {
                var cmd = Console.ReadLine()?.ToLower();
                if (cmd == "start" && !gameInProgress && clients.Count > 0)
                {
                    StartGame();
                }
                else if (cmd == "start" && clients.Count == 0)
                {
                    Console.WriteLine("No players connected yet. Wait for players to join.");
                }
                else if (cmd == "start" && gameInProgress)
                {
                    Console.WriteLine("Game already in progress.");
                }
                else if (cmd == "quit")
                {
                    Console.WriteLine("Shutting down server...");
                    listener?.Stop();
                    Environment.Exit(0);
                }
            }
        }

        private async void StartGame()
        {
            gameInProgress = true;
            currentQuestion = 0;
            scores.Clear();

            Console.WriteLine($"\n=== GAME STARTING with {clients.Count} players ===\n");
            BroadcastMessage("GAME_START");
            await Task.Delay(2000);

            while (currentQuestion < questions.Count)
            {
                await AskQuestion();
                currentQuestion++;
            }

            ShowFinalScores();
            gameInProgress = false;
            Console.WriteLine("\nGame ended. Type 'start' to begin a new game.");
        }

        private async Task AskQuestion()
        {
            var q = questions[currentQuestion];
            var msg = $"QUESTION|{currentQuestion + 1}|{q.Text}|{string.Join("|", q.Options)}";

            Console.WriteLine($"\nQuestion {currentQuestion + 1}: {q.Text}");
            foreach (var c in clients)
            {
                c.ClearAnswer();
            }

            BroadcastMessage(msg);

            var startTime = DateTime.Now;
            await Task.Delay(ANSWER_TIME * 1000);

            // Calculate scores
            foreach (var c in clients)
            {
                if (c.Answer == q.CorrectIndex)
                {
                    var timeTaken = (c.AnswerTime - startTime).TotalSeconds;
                    var points = Math.Max(100 - (int)(timeTaken * 5), 50);

                    if (!scores.ContainsKey(c.PlayerName))
                        scores[c.PlayerName] = 0;
                    scores[c.PlayerName] += points;

                    Console.WriteLine($"  {c.PlayerName}: Correct! (+{points} pts)");
                }
                else if (c.Answer != -1)
                {
                    Console.WriteLine($"  {c.PlayerName}: Incorrect");
                }
                else
                {
                    Console.WriteLine($"  {c.PlayerName}: No answer");
                }
            }

            BroadcastMessage($"ANSWER|{q.CorrectIndex}|{q.Options[q.CorrectIndex]}");
            await Task.Delay(3000);
        }

        private void ShowFinalScores()
        {
            Console.WriteLine("\n=== FINAL SCORES ===");
            var sorted = scores.OrderByDescending(x => x.Value).ToList();
            var scoreMsg = "SCORES|" + string.Join("|", sorted.Select(x => $"{x.Key}:{x.Value}"));

            for (int i = 0; i < sorted.Count; i++)
            {
                Console.WriteLine($"{i + 1}. {sorted[i].Key}: {sorted[i].Value} points");
            }

            BroadcastMessage(scoreMsg);
        }

        public void BroadcastMessage(string msg)
        {
            foreach (var c in clients.ToList())
            {
                c.SendMessage(msg);
            }
        }

        public void RemoveClient(ClientHandler client)
        {
            clients.Remove(client);
            Console.WriteLine($"Player {client.PlayerName} disconnected");
        }
    }

    public class ClientHandler
    {
        private TcpClient client;
        private NetworkStream stream;
        private QuizServer server;
        public string PlayerName { get; private set; }
        public int Answer { get; private set; } = -1;
        public DateTime AnswerTime { get; private set; }

        public ClientHandler(TcpClient client, QuizServer server)
        {
            this.client = client;
            this.server = server;
            this.stream = client.GetStream();
        }

        public void ClearAnswer()
        {
            Answer = -1;
        }

        public async Task HandleClient()
        {
            try
            {
                byte[] buffer = new byte[1024];
                int bytes = await stream.ReadAsync(buffer, 0, buffer.Length);
                PlayerName = Encoding.UTF8.GetString(buffer, 0, bytes);

                Console.WriteLine($"Player '{PlayerName}' connected!");
                SendMessage($"WELCOME|{PlayerName}");

                while (true)
                {
                    bytes = await stream.ReadAsync(buffer, 0, buffer.Length);
                    if (bytes == 0) break;

                    var msg = Encoding.UTF8.GetString(buffer, 0, bytes);
                    if (msg.StartsWith("ANSWER|"))
                    {
                        Answer = int.Parse(msg.Split('|')[1]);
                        AnswerTime = DateTime.Now;
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Client error: {ex.Message}");
            }
            finally
            {
                server.RemoveClient(this);
                client.Close();
            }
        }

        public void SendMessage(string msg)
        {
            try
            {
                byte[] data = Encoding.UTF8.GetBytes(msg);
                stream.Write(data, 0, data.Length);
            }
            catch { }
        }
    }

    public class Question
    {
        public string Text { get; set; }
        public string[] Options { get; set; }
        public int CorrectIndex { get; set; }

        public Question(string text, string[] options, int correctIndex)
        {
            Text = text;
            Options = options;
            CorrectIndex = correctIndex;
        }
    }
}