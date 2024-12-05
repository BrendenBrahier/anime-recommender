using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Diagnostics.Eventing.Reader;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Diagnostics;
using System.IO;
using System.Net.Http;

namespace YAMWebForm
{
    public partial class searchForm : Form
    {
        public searchForm()
        {
            InitializeComponent();
        }

        private List<recommendedAnimeBN> FilterRecommendations(string recommendations)
        {
            List<recommendedAnimeBN> filteredAnime = new List<recommendedAnimeBN>();
            var animeLines = recommendations.Split(new[] { "\n" }, StringSplitOptions.RemoveEmptyEntries);

            foreach (var line in animeLines)
            {
                if (line.StartsWith("No recommendations found."))
                {
                    continue;
                }

                string[] tokens = line.Split(new[] { " - " }, StringSplitOptions.None);
                if (tokens.Length >= 5)
                {
                    var filteredRecAnime = new recommendedAnimeBN
                    {
                        name = tokens[0].Substring(2).Trim(),
                        imageURL = tokens[1].Trim(),
                        genres = tokens[2].Trim(),
                        rating = tokens[3].Trim(),
                        year = tokens[4].Trim()
                    };

                    filteredAnime.Add(filteredRecAnime);
                }
            }

            return filteredAnime;
        }

        private void runGraphRecs()
        {
            string pythonScript = @"C:\\Users\\trentford\\source\\repos\\YAMWebForm\\YAMWebForm\\graph_recommendations.py";

            if (!File.Exists(pythonScript))
            {
                MessageBox.Show("Python script not found: " + pythonScript);
                return;
            }

            ProcessStartInfo psi = new ProcessStartInfo();

            psi.FileName = @"C:\Users\trentford\AppData\Local\Programs\Python\Python313\python.exe";
            psi.Arguments = $"\"{pythonScript}\" \"{searchTextbox.Text}\" {numResultsNUD.Value}";
            psi.UseShellExecute = false;
            psi.CreateNoWindow = true;
            psi.RedirectStandardOutput = true;
            psi.RedirectStandardError = true;
            Process process = new Process();
            process.StartInfo = psi;

            try
            {
                process.Start();
                string standardOutput = process.StandardOutput.ReadToEnd();
                string standardError = process.StandardError.ReadToEnd();
                process.WaitForExit();

                if (standardError != "")
                {
                    MessageBox.Show("An error occurred: " + standardError);
                    return;
                }

                List<recommendedAnimeBN> recommendedAnimeGraph = FilterRecommendations(standardOutput);
                recsDGV.DataSource = recommendedAnimeGraph;

            }
            catch(Exception ex)
            {
                MessageBox.Show("An error occurred: " + ex.Message);
            }
        }

        private void runHashRecs()
        {
            string pythonScript = @"C:\\Users\\trentford\\source\\repos\\YAMWebForm\\YAMWebForm\\hashmap_recommendations.py";


            if (!File.Exists(pythonScript))
            {
                MessageBox.Show("Python script not found: " + pythonScript);
                return;
            }

            ProcessStartInfo psi = new ProcessStartInfo();

            psi.FileName = @"C:\Users\trentford\AppData\Local\Programs\Python\Python313\python.exe";
            psi.Arguments = $"{pythonScript} \"{searchTextbox.Text}\" {numResultsNUD.Value}";
            psi.UseShellExecute = false;
            psi.CreateNoWindow = true;
            psi.RedirectStandardOutput = true;
            psi.RedirectStandardError = true;
            Process process = new Process();
            process.StartInfo = psi;

            try
            {
                process.Start();
                string standardOutput = process.StandardOutput.ReadToEnd();
                string standardError = process.StandardError.ReadToEnd();
                process.WaitForExit();

                if (standardError != "")
                {
                    MessageBox.Show("An error occurred: " + standardError);
                    return;
                }

                List<recommendedAnimeBN> recommendedAnimeHashmap = FilterRecommendations(standardOutput);
                recsDGV.DataSource = recommendedAnimeHashmap;

            }
            catch (Exception ex)
            {
                MessageBox.Show("An error occurred: " + ex.Message);
            }
        }

        private void sbcLabel_Click(object sender, EventArgs e)
        {
            SearchByCategories sbcForm = new SearchByCategories();
            sbcForm.Show();
        }

        private void recsButton_Click(object sender, EventArgs e)
        {
            //Ensure all fields are filled
            if (searchTextbox.Text.Length == 0 || numResultsNUD.Value == 0 || (!hashmapRB.Checked && !graphRB.Checked))
            {
                if (searchTextbox.Text.Length == 0)
                {
                    notInListEP.SetError(this.searchTextbox, "Please Enter an Anime.");
                }
                else
                {
                    notInListEP.SetError(this.searchTextbox, "");
                }

                if (numResultsNUD.Value == 0)
                {
                    noResultsEP.SetError(this.numResultsNUD, "Please Enter a Number of Results to be Displayed.");
                }
                else
                {
                    noResultsEP.SetError(this.numResultsNUD, "");
                }

                if (!hashmapRB.Checked && !graphRB.Checked)
                {
                    noSearchEP.SetError(this.searchWithLabel, "Please Select a Data Structure Type.");
                }
                else
                {
                    noSearchEP.SetError(this.searchWithLabel, "");
                }
            }
            //Make recommendations if entries given
            else
            {
                    notInListEP.SetError(this.searchTextbox, "");
                    noResultsEP.SetError(this.numResultsNUD, "");
                    noSearchEP.SetError(this.searchWithLabel, "");
                //Do the stuff
                if (graphRB.Checked)
                { 
                    runGraphRecs();
                }
                if (hashmapRB.Checked)
                {
                    runHashRecs();
                }
            }
        }
    }

    public class recommendedAnimeBN
    {
        public string name { get; set; }
        public string imageURL { get; set; }
        public string genres { get; set; }
        public string rating { get; set; }
        public string year { get; set; }
    }
}
