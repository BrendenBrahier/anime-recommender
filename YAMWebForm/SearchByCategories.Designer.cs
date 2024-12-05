namespace YAMWebForm
{
    partial class SearchByCategories
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.components = new System.ComponentModel.Container();
            this.titleLabel = new System.Windows.Forms.Label();
            this.genreLabel = new System.Windows.Forms.Label();
            this.genreListbox = new System.Windows.Forms.ListBox();
            this.yearLabel = new System.Windows.Forms.Label();
            this.ratingLabel = new System.Windows.Forms.Label();
            this.popLabel = new System.Windows.Forms.Label();
            this.yearListbox = new System.Windows.Forms.ListBox();
            this.ratingListbox = new System.Windows.Forms.ListBox();
            this.popListbox = new System.Windows.Forms.ListBox();
            this.somLabel = new System.Windows.Forms.Label();
            this.recsDGV = new System.Windows.Forms.DataGridView();
            this.imageCol = new System.Windows.Forms.DataGridViewImageColumn();
            this.animeName = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.genreCol = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.ratingCol = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.yearCol = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.recsButton = new System.Windows.Forms.Button();
            this.noGenreEP = new System.Windows.Forms.ErrorProvider(this.components);
            this.noYearEP = new System.Windows.Forms.ErrorProvider(this.components);
            this.noRatingEP = new System.Windows.Forms.ErrorProvider(this.components);
            this.noPopEP = new System.Windows.Forms.ErrorProvider(this.components);
            this.nosomEP = new System.Windows.Forms.ErrorProvider(this.components);
            this.searchWithLabel = new System.Windows.Forms.Label();
            this.hashmapRB = new System.Windows.Forms.RadioButton();
            this.graphRB = new System.Windows.Forms.RadioButton();
            this.noSearchEP = new System.Windows.Forms.ErrorProvider(this.components);
            this.numResultsNUD = new System.Windows.Forms.NumericUpDown();
            this.numResultsLabel = new System.Windows.Forms.Label();
            this.noResultsEP = new System.Windows.Forms.ErrorProvider(this.components);
            this.typeListbox = new System.Windows.Forms.ListBox();
            ((System.ComponentModel.ISupportInitialize)(this.recsDGV)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.noGenreEP)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.noYearEP)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.noRatingEP)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.noPopEP)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.nosomEP)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.noSearchEP)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.numResultsNUD)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.noResultsEP)).BeginInit();
            this.SuspendLayout();
            // 
            // titleLabel
            // 
            this.titleLabel.AutoSize = true;
            this.titleLabel.Font = new System.Drawing.Font("Segoe Print", 24F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.titleLabel.Location = new System.Drawing.Point(664, 74);
            this.titleLabel.Name = "titleLabel";
            this.titleLabel.Size = new System.Drawing.Size(609, 112);
            this.titleLabel.TabIndex = 10;
            this.titleLabel.Text = "YourAnimeMatch";
            // 
            // genreLabel
            // 
            this.genreLabel.AutoSize = true;
            this.genreLabel.Font = new System.Drawing.Font("Segoe Print", 16.125F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.genreLabel.Location = new System.Drawing.Point(101, 195);
            this.genreLabel.Name = "genreLabel";
            this.genreLabel.Size = new System.Drawing.Size(160, 75);
            this.genreLabel.TabIndex = 13;
            this.genreLabel.Text = "Genre";
            // 
            // genreListbox
            // 
            this.genreListbox.Font = new System.Drawing.Font("Microsoft Sans Serif", 10.125F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.genreListbox.FormattingEnabled = true;
            this.genreListbox.ItemHeight = 31;
            this.genreListbox.Items.AddRange(new object[] {
            "Action",
            "Adventure",
            "Avant Garde",
            "Award Winning",
            "Boys Love",
            "Comedy",
            "Cyberpunk",
            "Drama",
            "Ecchi",
            "Erotica",
            "Fantasy",
            "Girls Love",
            "Gourmet",
            "Harem",
            "Hentai",
            "Historical",
            "Horror",
            "Isekai",
            "Josei",
            "Martial Arts",
            "Mecha",
            "Music",
            "Mystery",
            "Post-Apocalyptic",
            "Psychological",
            "Romance",
            "School",
            "Sci-Fi",
            "Science Fiction",
            "Seinen",
            "Shoujo",
            "Shounen",
            "Slice of Life",
            "Sports",
            "Supernatural",
            "Suspense",
            "Thriller"});
            this.genreListbox.Location = new System.Drawing.Point(38, 291);
            this.genreListbox.Name = "genreListbox";
            this.genreListbox.SelectionMode = System.Windows.Forms.SelectionMode.MultiSimple;
            this.genreListbox.Size = new System.Drawing.Size(301, 190);
            this.genreListbox.TabIndex = 14;
            // 
            // yearLabel
            // 
            this.yearLabel.AutoSize = true;
            this.yearLabel.Font = new System.Drawing.Font("Segoe Print", 16.125F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.yearLabel.Location = new System.Drawing.Point(514, 195);
            this.yearLabel.Name = "yearLabel";
            this.yearLabel.Size = new System.Drawing.Size(130, 75);
            this.yearLabel.TabIndex = 15;
            this.yearLabel.Text = "Year";
            // 
            // ratingLabel
            // 
            this.ratingLabel.AutoSize = true;
            this.ratingLabel.Font = new System.Drawing.Font("Segoe Print", 16.125F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.ratingLabel.Location = new System.Drawing.Point(888, 195);
            this.ratingLabel.Name = "ratingLabel";
            this.ratingLabel.Size = new System.Drawing.Size(174, 75);
            this.ratingLabel.TabIndex = 17;
            this.ratingLabel.Text = "Rating";
            // 
            // popLabel
            // 
            this.popLabel.AutoSize = true;
            this.popLabel.Font = new System.Drawing.Font("Segoe Print", 16.125F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.popLabel.Location = new System.Drawing.Point(1226, 195);
            this.popLabel.Name = "popLabel";
            this.popLabel.Size = new System.Drawing.Size(256, 75);
            this.popLabel.TabIndex = 19;
            this.popLabel.Text = "Popularity";
            // 
            // yearListbox
            // 
            this.yearListbox.Font = new System.Drawing.Font("Microsoft Sans Serif", 10.125F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.yearListbox.FormattingEnabled = true;
            this.yearListbox.ItemHeight = 31;
            this.yearListbox.Items.AddRange(new object[] {
            "1910-1920",
            "1920-1930",
            "1930-1940",
            "1940-1950",
            "1950-1960",
            "1960-1970",
            "1970-1980",
            "1980-1985",
            "1985-1990",
            "1990-1995",
            "1995-2000",
            "2000-2005",
            "2005-2010",
            "2010-2015",
            "2015-2020",
            "2020-2025"});
            this.yearListbox.Location = new System.Drawing.Point(439, 291);
            this.yearListbox.Name = "yearListbox";
            this.yearListbox.SelectionMode = System.Windows.Forms.SelectionMode.MultiSimple;
            this.yearListbox.Size = new System.Drawing.Size(301, 190);
            this.yearListbox.TabIndex = 20;
            // 
            // ratingListbox
            // 
            this.ratingListbox.Font = new System.Drawing.Font("Microsoft Sans Serif", 10.125F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.ratingListbox.FormattingEnabled = true;
            this.ratingListbox.ItemHeight = 31;
            this.ratingListbox.Items.AddRange(new object[] {
            "0.00-0.99",
            "1.00-1.99",
            "2.00-2.99",
            "3.00-3.99",
            "4.00-4.99",
            "5.00-5.49",
            "5.50-5.99",
            "6.00-6.49",
            "6.50-6.99",
            "7.00-7.49",
            "7.50-7.99",
            "8.00-8.99",
            "9.00-10.00"});
            this.ratingListbox.Location = new System.Drawing.Point(827, 291);
            this.ratingListbox.Name = "ratingListbox";
            this.ratingListbox.SelectionMode = System.Windows.Forms.SelectionMode.MultiSimple;
            this.ratingListbox.Size = new System.Drawing.Size(301, 190);
            this.ratingListbox.TabIndex = 21;
            // 
            // popListbox
            // 
            this.popListbox.Font = new System.Drawing.Font("Microsoft Sans Serif", 10.125F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.popListbox.FormattingEnabled = true;
            this.popListbox.ItemHeight = 31;
            this.popListbox.Items.AddRange(new object[] {
            "0-100",
            "101-249",
            "250-499",
            "500-999",
            "1000-2499",
            "2500-4999",
            "5000-7499",
            "7500-9999",
            "10000+"});
            this.popListbox.Location = new System.Drawing.Point(1204, 291);
            this.popListbox.Name = "popListbox";
            this.popListbox.SelectionMode = System.Windows.Forms.SelectionMode.MultiSimple;
            this.popListbox.Size = new System.Drawing.Size(301, 190);
            this.popListbox.TabIndex = 22;
            // 
            // somLabel
            // 
            this.somLabel.AutoSize = true;
            this.somLabel.Font = new System.Drawing.Font("Segoe Print", 16.125F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.somLabel.Location = new System.Drawing.Point(1521, 195);
            this.somLabel.Name = "somLabel";
            this.somLabel.Size = new System.Drawing.Size(357, 75);
            this.somLabel.TabIndex = 25;
            this.somLabel.Text = "Series or Movie";
            // 
            // recsDGV
            // 
            this.recsDGV.BackgroundColor = System.Drawing.Color.LightGoldenrodYellow;
            this.recsDGV.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.recsDGV.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
            this.imageCol,
            this.animeName,
            this.genreCol,
            this.ratingCol,
            this.yearCol});
            this.recsDGV.Location = new System.Drawing.Point(514, 553);
            this.recsDGV.Name = "recsDGV";
            this.recsDGV.RowHeadersWidth = 82;
            this.recsDGV.RowTemplate.Height = 33;
            this.recsDGV.Size = new System.Drawing.Size(1364, 444);
            this.recsDGV.TabIndex = 26;
            // 
            // imageCol
            // 
            this.imageCol.HeaderText = "Image";
            this.imageCol.MinimumWidth = 10;
            this.imageCol.Name = "imageCol";
            this.imageCol.Width = 480;
            // 
            // animeName
            // 
            this.animeName.HeaderText = "Anime Name";
            this.animeName.MinimumWidth = 10;
            this.animeName.Name = "animeName";
            this.animeName.Width = 200;
            // 
            // genreCol
            // 
            this.genreCol.HeaderText = "Genre";
            this.genreCol.MinimumWidth = 10;
            this.genreCol.Name = "genreCol";
            this.genreCol.Width = 200;
            // 
            // ratingCol
            // 
            this.ratingCol.HeaderText = "Rating";
            this.ratingCol.MinimumWidth = 10;
            this.ratingCol.Name = "ratingCol";
            this.ratingCol.Width = 200;
            // 
            // yearCol
            // 
            this.yearCol.HeaderText = "Year";
            this.yearCol.MinimumWidth = 10;
            this.yearCol.Name = "yearCol";
            this.yearCol.Width = 200;
            // 
            // recsButton
            // 
            this.recsButton.BackColor = System.Drawing.Color.DarkSeaGreen;
            this.recsButton.Font = new System.Drawing.Font("Segoe Print", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.recsButton.Location = new System.Drawing.Point(64, 745);
            this.recsButton.Name = "recsButton";
            this.recsButton.Size = new System.Drawing.Size(341, 252);
            this.recsButton.TabIndex = 27;
            this.recsButton.Text = "Get Recommendations";
            this.recsButton.UseVisualStyleBackColor = false;
            this.recsButton.Click += new System.EventHandler(this.recsButton_Click);
            // 
            // noGenreEP
            // 
            this.noGenreEP.ContainerControl = this;
            // 
            // noYearEP
            // 
            this.noYearEP.ContainerControl = this;
            // 
            // noRatingEP
            // 
            this.noRatingEP.ContainerControl = this;
            // 
            // noPopEP
            // 
            this.noPopEP.ContainerControl = this;
            // 
            // nosomEP
            // 
            this.nosomEP.ContainerControl = this;
            // 
            // searchWithLabel
            // 
            this.searchWithLabel.AutoSize = true;
            this.searchWithLabel.Font = new System.Drawing.Font("Segoe Print", 16.125F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.searchWithLabel.Location = new System.Drawing.Point(85, 553);
            this.searchWithLabel.Name = "searchWithLabel";
            this.searchWithLabel.Size = new System.Drawing.Size(297, 75);
            this.searchWithLabel.TabIndex = 28;
            this.searchWithLabel.Text = "Search With";
            // 
            // hashmapRB
            // 
            this.hashmapRB.AutoSize = true;
            this.hashmapRB.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.hashmapRB.Location = new System.Drawing.Point(140, 631);
            this.hashmapRB.Name = "hashmapRB";
            this.hashmapRB.Size = new System.Drawing.Size(186, 41);
            this.hashmapRB.TabIndex = 29;
            this.hashmapRB.TabStop = true;
            this.hashmapRB.Text = "Hashmap";
            this.hashmapRB.UseVisualStyleBackColor = true;
            // 
            // graphRB
            // 
            this.graphRB.AutoSize = true;
            this.graphRB.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.graphRB.Location = new System.Drawing.Point(140, 678);
            this.graphRB.Name = "graphRB";
            this.graphRB.Size = new System.Drawing.Size(138, 41);
            this.graphRB.TabIndex = 31;
            this.graphRB.TabStop = true;
            this.graphRB.Text = "Graph";
            this.graphRB.UseVisualStyleBackColor = true;
            // 
            // noSearchEP
            // 
            this.noSearchEP.ContainerControl = this;
            // 
            // numResultsNUD
            // 
            this.numResultsNUD.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.numResultsNUD.Location = new System.Drawing.Point(1603, 487);
            this.numResultsNUD.Name = "numResultsNUD";
            this.numResultsNUD.Size = new System.Drawing.Size(158, 44);
            this.numResultsNUD.TabIndex = 33;
            // 
            // numResultsLabel
            // 
            this.numResultsLabel.AutoSize = true;
            this.numResultsLabel.Font = new System.Drawing.Font("Segoe Print", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.numResultsLabel.Location = new System.Drawing.Point(1524, 428);
            this.numResultsLabel.Name = "numResultsLabel";
            this.numResultsLabel.Size = new System.Drawing.Size(333, 56);
            this.numResultsLabel.TabIndex = 32;
            this.numResultsLabel.Text = "Number of Results:";
            // 
            // noResultsEP
            // 
            this.noResultsEP.ContainerControl = this;
            // 
            // typeListbox
            // 
            this.typeListbox.Font = new System.Drawing.Font("Microsoft Sans Serif", 10.125F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.typeListbox.FormattingEnabled = true;
            this.typeListbox.ItemHeight = 31;
            this.typeListbox.Items.AddRange(new object[] {
            "TV Series",
            "Movie",
            "OVA"});
            this.typeListbox.Location = new System.Drawing.Point(1550, 302);
            this.typeListbox.Name = "typeListbox";
            this.typeListbox.Size = new System.Drawing.Size(306, 97);
            this.typeListbox.TabIndex = 34;
            // 
            // SearchByCategories
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(12F, 25F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.BackColor = System.Drawing.Color.LightGoldenrodYellow;
            this.ClientSize = new System.Drawing.Size(1894, 1009);
            this.Controls.Add(this.typeListbox);
            this.Controls.Add(this.numResultsNUD);
            this.Controls.Add(this.numResultsLabel);
            this.Controls.Add(this.graphRB);
            this.Controls.Add(this.hashmapRB);
            this.Controls.Add(this.searchWithLabel);
            this.Controls.Add(this.recsButton);
            this.Controls.Add(this.recsDGV);
            this.Controls.Add(this.somLabel);
            this.Controls.Add(this.popListbox);
            this.Controls.Add(this.ratingListbox);
            this.Controls.Add(this.yearListbox);
            this.Controls.Add(this.popLabel);
            this.Controls.Add(this.ratingLabel);
            this.Controls.Add(this.yearLabel);
            this.Controls.Add(this.genreListbox);
            this.Controls.Add(this.genreLabel);
            this.Controls.Add(this.titleLabel);
            this.Name = "SearchByCategories";
            this.Text = "Search Anime Based on Categories";
            ((System.ComponentModel.ISupportInitialize)(this.recsDGV)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.noGenreEP)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.noYearEP)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.noRatingEP)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.noPopEP)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.nosomEP)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.noSearchEP)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.numResultsNUD)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.noResultsEP)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion
        private System.Windows.Forms.Label titleLabel;
        private System.Windows.Forms.Label genreLabel;
        private System.Windows.Forms.ListBox genreListbox;
        private System.Windows.Forms.Label yearLabel;
        private System.Windows.Forms.Label ratingLabel;
        private System.Windows.Forms.Label popLabel;
        private System.Windows.Forms.ListBox yearListbox;
        private System.Windows.Forms.ListBox ratingListbox;
        private System.Windows.Forms.ListBox popListbox;
        private System.Windows.Forms.Label somLabel;
        private System.Windows.Forms.DataGridView recsDGV;
        private System.Windows.Forms.DataGridViewImageColumn imageCol;
        private System.Windows.Forms.DataGridViewTextBoxColumn animeName;
        private System.Windows.Forms.DataGridViewTextBoxColumn genreCol;
        private System.Windows.Forms.DataGridViewTextBoxColumn ratingCol;
        private System.Windows.Forms.DataGridViewTextBoxColumn yearCol;
        private System.Windows.Forms.Button recsButton;
        private System.Windows.Forms.ErrorProvider noGenreEP;
        private System.Windows.Forms.ErrorProvider noYearEP;
        private System.Windows.Forms.ErrorProvider noRatingEP;
        private System.Windows.Forms.ErrorProvider noPopEP;
        private System.Windows.Forms.ErrorProvider nosomEP;
        private System.Windows.Forms.Label searchWithLabel;
        private System.Windows.Forms.RadioButton graphRB;
        private System.Windows.Forms.RadioButton hashmapRB;
        private System.Windows.Forms.ErrorProvider noSearchEP;
        private System.Windows.Forms.NumericUpDown numResultsNUD;
        private System.Windows.Forms.Label numResultsLabel;
        private System.Windows.Forms.ErrorProvider noResultsEP;
        private System.Windows.Forms.ListBox typeListbox;
    }
}