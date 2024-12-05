using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
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
    public partial class SearchByCategories : Form
    {
        public SearchByCategories()
        {
            InitializeComponent();
        }

        private List<recommendedAnimeBC> FilterRecommendations(string recommendations)
        {
            List<recommendedAnimeBC> filteredAnime = new List<recommendedAnimeBC>();
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
                    var filteredRecAnime = new recommendedAnimeBC
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

        private void runGraphRecsBC()
        {
            string pythonScript = @"C:\\Users\\trentford\\source\\repos\\YAMWebForm\\YAMWebForm\\graph_recommendations.py";

            if (!File.Exists(pythonScript))
            {
                MessageBox.Show("Python script not found: " + pythonScript);
                return;
            }

            ProcessStartInfo psi = new ProcessStartInfo();

            psi.FileName = @"C:\Users\trentford\AppData\Local\Programs\Python\Python313\python.exe";
            psi.Arguments = $"\"{pythonScript}\" \"{genreListbox.SelectedValue}\" \"{yearListbox.SelectedValue}\" \"{ratingListbox.SelectedValue}\" \"{popListbox.SelectedValue}\" \"{typeListbox.SelectedValue}\" {numResultsNUD.Value}";
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

                List<recommendedAnimeBC> recommendedAnimeGraph = FilterRecommendations(standardOutput);
                recsDGV.DataSource = recommendedAnimeGraph;

            }
            catch (Exception ex)
            {
                MessageBox.Show("An error occurred: " + ex.Message);
            }
        }

        private void runHashRecsBC()
        {
            string pythonScript = @"C:\\Users\\trentford\\source\\repos\\YAMWebForm\\YAMWebForm\\hashmap_recommendations.py";


            if (!File.Exists(pythonScript))
            {
                MessageBox.Show("Python script not found: " + pythonScript);
                return;
            }

            ProcessStartInfo psi = new ProcessStartInfo();

            psi.FileName = @"C:\Users\trentford\AppData\Local\Programs\Python\Python313\python.exe";
            psi.Arguments = $"\"{pythonScript}\" \"{genreListbox.SelectedValue}\" \"{yearListbox.SelectedValue}\" \"{ratingListbox.SelectedValue}\" \"{popListbox.SelectedValue}\" \"{typeListbox.SelectedValue}\" {numResultsNUD.Value}";
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

                List<recommendedAnimeBC> recommendedAnimeHashmap = FilterRecommendations(standardOutput);
                recsDGV.DataSource = recommendedAnimeHashmap;

            }
            catch (Exception ex)
            {
                MessageBox.Show("An error occurred: " + ex.Message);
            }
        }

        private void recsButton_Click(object sender, EventArgs e)
        {
            //Check if all categories selected, giving an error to those wthat aren't and clearing if a choice has been made
            //after a second click
            if (genreListbox.SelectedIndex == -1 || yearListbox.SelectedIndex == -1 || ratingListbox.SelectedIndex == -1 ||
                popListbox.SelectedIndex == -1 || typeListbox.SelectedIndex == -1 || (!hashmapRB.Checked && !graphRB.Checked) || numResultsNUD.Value == 0)
            {
                if (genreListbox.SelectedIndex == -1)
                {
                    noGenreEP.SetError(this.genreLabel, "Please Select a Genre.");
                }
                else
                {
                    noGenreEP.SetError(this.genreLabel, "");
                }

                if (yearListbox.SelectedIndex == -1)
                {
                    noYearEP.SetError(this.yearLabel, "Please Select a Year Range.");
                }
                else
                {
                    noYearEP.SetError(this.yearLabel, "");
                }

                if (ratingListbox.SelectedIndex == -1)
                {
                    noRatingEP.SetError(this.ratingLabel, "Please Select a Rating Range.");
                }
                else
                {
                    noRatingEP.SetError(this.ratingLabel, "");
                }

                if (popListbox.SelectedIndex == -1)
                {
                    noPopEP.SetError(this.popLabel, "Please Select a Populuartiy Based On Members Watched Range.");
                }
                else
                {
                    noPopEP.SetError(this.popLabel, "");
                }

                if (typeListbox.SelectedIndex == -1)
                {
                    nosomEP.SetError(this.somLabel, "Please Select TV Series or Movie.");
                }
                else
                {
                    nosomEP.SetError(this.somLabel, "");
                }

                if (!hashmapRB.Checked && !graphRB.Checked)
                {
                    noSearchEP.SetError(this.searchWithLabel, "Please Select a Search Type.");
                }
                else
                {
                    noSearchEP.SetError(this.searchWithLabel, "");
                }

                if (numResultsNUD.Value == 0)
                {
                    noResultsEP.SetError(this.numResultsLabel, "Please Enter a Number of Results to be Displayed.");
                }
                else
                {
                    noResultsEP.SetError(this.numResultsLabel, "");
                }
            }
            else
            {
                noGenreEP.SetError(this.genreLabel, "");
                noYearEP.SetError(this.yearLabel, "");
                noRatingEP.SetError(this.ratingLabel, "");
                noPopEP.SetError(this.popLabel, "");
                nosomEP.SetError(this.somLabel, "");
                noSearchEP.SetError(this.searchWithLabel, "");
                noResultsEP.SetError(this.numResultsLabel, "");
                

                if(graphRB.Checked)
                {
                    runGraphRecsBC();
                }
                if(hashmapRB.Checked)
                {
                    runHashRecsBC();
                }
            }
        }
    }

    public class recommendedAnimeBC
    {
        public string name { get; set; }
        public string imageURL { get; set; }
        public string genres { get; set; }
        public string rating { get; set; }
        public string year { get; set; }
    }
}
