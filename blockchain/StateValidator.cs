// orbital-agent/src/blockchain/StateValidator.cs
using System;
using System.Security.Cryptography;
using System.Text;

namespace Orbital.Blockchain
{
    public class MerkleValidator
    {
        public static string CalculateMerkleRoot(string[] transactions)
        {
            using SHA256 sha256 = SHA256.Create();
            List<string> tree = new List<string>(transactions);
            
            while (tree.Count > 1)
            {
                List<string> newLevel = new List<string>();
                for (int i = 0; i < tree.Count; i += 2)
                {
                    string combined = i + 1 < tree.Count ? 
                        tree[i] + tree[i + 1] : tree[i];
                    byte[] hash = sha256.ComputeHash(Encoding.UTF8.GetBytes(combined));
                    newLevel.Add(BitConverter.ToString(hash).Replace("-", ""));
                }
                tree = newLevel;
            }
            return tree.FirstOrDefault() ?? string.Empty;
        }
    }
}
