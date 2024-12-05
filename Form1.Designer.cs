namespace YAMWebForm
{
    partial class searchForm
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
            this.instrLabel = new System.Windows.Forms.Label();
            this.numResultsLabel = new System.Windows.Forms.Label();
            this.numResultsNUD = new System.Windows.Forms.NumericUpDown();
            this.recsDGV = new System.Windows.Forms.DataGridView();
            this.sbcLabel = new System.Windows.Forms.Label();
            this.recsButton = new System.Windows.Forms.Button();
            this.notInListEP = new System.Windows.Forms.ErrorProvider(this.components);
            this.noResultsEP = new System.Windows.Forms.ErrorProvider(this.components);
            this.graphRB = new System.Windows.Forms.RadioButton();
            this.hashmapRB = new System.Windows.Forms.RadioButton();
            this.searchWithLabel = new System.Windows.Forms.Label();
            this.noSearchEP = new System.Windows.Forms.ErrorProvider(this.components);
            this.searchTextbox = new System.Windows.Forms.TextBox();
            this.animeName = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.imageCol = new System.Windows.Forms.DataGridViewImageColumn();
            this.genreCol = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.ratingCol = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.yearCol = new System.Windows.Forms.DataGridViewTextBoxColumn();
            ((System.ComponentModel.ISupportInitialize)(this.numResultsNUD)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.recsDGV)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.notInListEP)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.noResultsEP)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.noSearchEP)).BeginInit();
            this.SuspendLayout();
            // 
            // titleLabel
            // 
            this.titleLabel.AutoSize = true;
            this.titleLabel.Font = new System.Drawing.Font("Segoe Print", 24F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.titleLabel.Location = new System.Drawing.Point(682, 60);
            this.titleLabel.Name = "titleLabel";
            this.titleLabel.Size = new System.Drawing.Size(609, 112);
            this.titleLabel.TabIndex = 1;
            this.titleLabel.Text = "YourAnimeMatch";
            // 
            // instrLabel
            // 
            this.instrLabel.AutoSize = true;
            this.instrLabel.Font = new System.Drawing.Font("Segoe Print", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.instrLabel.Location = new System.Drawing.Point(409, 172);
            this.instrLabel.Name = "instrLabel";
            this.instrLabel.Size = new System.Drawing.Size(1128, 56);
            this.instrLabel.TabIndex = 2;
            this.instrLabel.Text = "Start with an anime you like and we will give you more suggestions";
            // 
            // numResultsLabel
            // 
            this.numResultsLabel.AutoSize = true;
            this.numResultsLabel.Font = new System.Drawing.Font("Segoe Print", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.numResultsLabel.Location = new System.Drawing.Point(409, 348);
            this.numResultsLabel.Name = "numResultsLabel";
            this.numResultsLabel.Size = new System.Drawing.Size(333, 56);
            this.numResultsLabel.TabIndex = 4;
            this.numResultsLabel.Text = "Number of Results:";
            // 
            // numResultsNUD
            // 
            this.numResultsNUD.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.numResultsNUD.Location = new System.Drawing.Point(748, 357);
            this.numResultsNUD.Name = "numResultsNUD";
            this.numResultsNUD.Size = new System.Drawing.Size(158, 44);
            this.numResultsNUD.TabIndex = 5;
            // 
            // recsDGV
            // 
            this.recsDGV.BackgroundColor = System.Drawing.Color.LightGoldenrodYellow;
            this.recsDGV.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.recsDGV.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
            this.animeName,
            this.imageCol,
            this.genreCol,
            this.ratingCol,
            this.yearCol});
            this.recsDGV.Location = new System.Drawing.Point(467, 502);
            this.recsDGV.Name = "recsDGV";
            this.recsDGV.RowHeadersWidth = 82;
            this.recsDGV.RowTemplate.Height = 33;
            this.recsDGV.Size = new System.Drawing.Size(1364, 444);
            this.recsDGV.TabIndex = 7;
            // 
            // sbcLabel
            // 
            this.sbcLabel.AutoSize = true;
            this.sbcLabel.Font = new System.Drawing.Font("Segoe Print", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.sbcLabel.ForeColor = System.Drawing.Color.DarkSeaGreen;
            this.sbcLabel.Location = new System.Drawing.Point(1171, 345);
            this.sbcLabel.Name = "sbcLabel";
            this.sbcLabel.Size = new System.Drawing.Size(366, 56);
            this.sbcLabel.TabIndex = 10;
            this.sbcLabel.Text = "Search By Categories";
            this.sbcLabel.Click += new System.EventHandler(this.sbcLabel_Click);
            // 
            // recsButton
            // 
            this.recsButton.BackColor = System.Drawing.Color.DarkSeaGreen;
            this.recsButton.Font = new System.Drawing.Font("Segoe Print", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.recsButton.Location = new System.Drawing.Point(50, 694);
            this.recsButton.Name = "recsButton";
            this.recsButton.Size = new System.Drawing.Size(341, 252);
            this.recsButton.TabIndex = 28;
            this.recsButton.Text = "Get Recommendations";
            this.recsButton.UseVisualStyleBackColor = false;
            this.recsButton.Click += new System.EventHandler(this.recsButton_Click);
            // 
            // notInListEP
            // 
            this.notInListEP.ContainerControl = this;
            // 
            // noResultsEP
            // 
            this.noResultsEP.ContainerControl = this;
            // 
            // graphRB
            // 
            this.graphRB.AutoSize = true;
            this.graphRB.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.graphRB.Location = new System.Drawing.Point(119, 627);
            this.graphRB.Name = "graphRB";
            this.graphRB.Size = new System.Drawing.Size(138, 41);
            this.graphRB.TabIndex = 34;
            this.graphRB.TabStop = true;
            this.graphRB.Text = "Graph";
            this.graphRB.UseVisualStyleBackColor = true;
            // 
            // hashmapRB
            // 
            this.hashmapRB.AutoSize = true;
            this.hashmapRB.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.hashmapRB.Location = new System.Drawing.Point(119, 580);
            this.hashmapRB.Name = "hashmapRB";
            this.hashmapRB.Size = new System.Drawing.Size(186, 41);
            this.hashmapRB.TabIndex = 33;
            this.hashmapRB.TabStop = true;
            this.hashmapRB.Text = "Hashmap";
            this.hashmapRB.UseVisualStyleBackColor = true;
            // 
            // searchWithLabel
            // 
            this.searchWithLabel.AutoSize = true;
            this.searchWithLabel.Font = new System.Drawing.Font("Segoe Print", 16.125F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.searchWithLabel.Location = new System.Drawing.Point(76, 502);
            this.searchWithLabel.Name = "searchWithLabel";
            this.searchWithLabel.Size = new System.Drawing.Size(297, 75);
            this.searchWithLabel.TabIndex = 32;
            this.searchWithLabel.Text = "Search With";
            // 
            // noSearchEP
            // 
            this.noSearchEP.ContainerControl = this;
            // 
            // searchTextbox
            // 
            this.searchTextbox.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.searchTextbox.Location = new System.Drawing.Point(419, 232);
            this.searchTextbox.Name = "searchTextbox";
            this.searchTextbox.Size = new System.Drawing.Size(1118, 44);
            this.searchTextbox.TabIndex = 35;
            // 
            // animeName
            // 
            this.animeName.HeaderText = "Anime Name";
            this.animeName.MinimumWidth = 10;
            this.animeName.Name = "animeName";
            this.animeName.Width = 200;
            // 
            // imageCol
            // 
            this.imageCol.HeaderText = "Image";
            this.imageCol.MinimumWidth = 10;
            this.imageCol.Name = "imageCol";
            this.imageCol.Width = 480;
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
            // searchForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(12F, 25F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.BackColor = System.Drawing.Color.LightGoldenrodYellow;
            this.ClientSize = new System.Drawing.Size(1894, 1009);
            this.Controls.Add(this.searchTextbox);
            this.Controls.Add(this.graphRB);
            this.Controls.Add(this.hashmapRB);
            this.Controls.Add(this.searchWithLabel);
            this.Controls.Add(this.recsButton);
            this.Controls.Add(this.sbcLabel);
            this.Controls.Add(this.recsDGV);
            this.Controls.Add(this.numResultsNUD);
            this.Controls.Add(this.numResultsLabel);
            this.Controls.Add(this.instrLabel);
            this.Controls.Add(this.titleLabel);
            this.Name = "searchForm";
            this.Text = "Search Anime Based on Previously Watched Anime";
            ((System.ComponentModel.ISupportInitialize)(this.numResultsNUD)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.recsDGV)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.notInListEP)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.noResultsEP)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.noSearchEP)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion
        private System.Windows.Forms.Label titleLabel;
        private System.Windows.Forms.Label instrLabel;
        private System.Windows.Forms.Label numResultsLabel;
        private System.Windows.Forms.NumericUpDown numResultsNUD;
        private System.Windows.Forms.DataGridView recsDGV;
        private System.Windows.Forms.Label sbcLabel;
        private System.Windows.Forms.Button recsButton;
        private System.Windows.Forms.ErrorProvider notInListEP;
        private System.Windows.Forms.ErrorProvider noResultsEP;
        private System.Windows.Forms.RadioButton graphRB;
        private System.Windows.Forms.RadioButton hashmapRB;
        private System.Windows.Forms.Label searchWithLabel;
        private System.Windows.Forms.ErrorProvider noSearchEP;
        private System.Windows.Forms.TextBox searchTextbox;
        private System.Windows.Forms.DataGridViewTextBoxColumn animeName;
        private System.Windows.Forms.DataGridViewImageColumn imageCol;
        private System.Windows.Forms.DataGridViewTextBoxColumn genreCol;
        private System.Windows.Forms.DataGridViewTextBoxColumn ratingCol;
        private System.Windows.Forms.DataGridViewTextBoxColumn yearCol;
    }
}

