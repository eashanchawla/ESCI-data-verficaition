"""
Purpose: Provide an interactive Jupyter widget for manual data labeling.
This file was written entirely using AI
"""
import pandas as pd
import ipywidgets as widgets
from IPython.display import display, HTML, clear_output
from pathlib import Path

class InteractiveLabeler:
    def __init__(self, df: pd.DataFrame, output_csv: str | Path):
        """
        Initializes the labeling widget.
        df: The dataframe containing the queries and product info.
        output_csv: Path to save the labeling progress.
        """
        self.df = df.copy()
        self.output_csv = Path(output_csv)
        
        # Load existing progress if the file exists
        if self.output_csv.exists():
            self.results_df = pd.read_csv(self.output_csv)
            labeled_ids = self.results_df['example_id'].tolist()
            self.df = self.df[~self.df['example_id'].isin(labeled_ids)].copy()
        else:
            self.results_df = pd.DataFrame(columns=['example_id', 'query', 'human_label', 'human_notes'])
            
        self.current_index = 0
        self.total_to_label = len(self.df)
        
        if self.total_to_label == 0:
            print("All items have been labeled! Check your output CSV.")
            return
            
        self.df = self.df.reset_index(drop=True)
        self._setup_ui()
        self._show_current()

    def _setup_ui(self):
        """Sets up the buttons and output areas."""
        self.output_area = widgets.Output()
        
        # Dropdown to select the correct label
        self.label_dropdown = widgets.Dropdown(
            options=['E (Exact)', 'S (Substitute)', 'C (Complement)', 'I (Irrelevant)', 'Skip'],
            value='E (Exact)',
            description='Correct Label:',
            disabled=False,
        )
        
        self.notes_box = widgets.Text(placeholder='Optional notes...', description='Notes:', layout=widgets.Layout(width='80%'))
        
        # Single submit button
        self.btn_submit = widgets.Button(description='Submit & Next', button_style='primary')
        self.btn_submit.on_click(self._handle_submit)
        
        # Layout
        self.controls_box = widgets.HBox([self.label_dropdown, self.btn_submit])
        self.main_ui = widgets.VBox([self.output_area, self.notes_box, self.controls_box])
        
        display(self.main_ui)

    def _show_current(self):
        """Renders the HTML for the current row."""
        if self.current_index >= self.total_to_label:
            with self.output_area:
                clear_output()
                display(HTML("<h3>Labeling Complete!</h3><p>All results saved to CSV.</p>"))
            self.controls_box.layout.display = 'none'
            self.notes_box.layout.display = 'none'
            return

        row = self.df.iloc[self.current_index]
        
        title = str(row.get('product_title', ''))
        bullets = str(row.get('product_bullet_point', ''))
        desc = str(row.get('product_description', ''))
        amazon_label = str(row.get('esci_label', 'Unknown'))
        brand = str(row.get('product_brand', 'Not specified'))
        color = str(row.get('product_color', 'Not specified'))
        
        # Pre-select the dropdown to match the original Amazon label
        if amazon_label in ['E', 'S', 'C', 'I']:
            # Find the full dropdown string that starts with the letter
            matching_option = next(opt for opt in self.label_dropdown.options if opt.startswith(amazon_label))
            self.label_dropdown.value = matching_option
        
        # Replace newlines with <br> for better HTML rendering
        bullets_html = bullets.replace('\n', '<br>')
        desc_html = desc.replace('\n', '<br>')
        
        html_content = f"""
        <div style='padding: 15px; border: 1px solid #ccc; border-radius: 5px; background-color: #f9f9f9;'>
            <h4>Progress: {self.current_index + 1} / {self.total_to_label}</h4>
            <hr>
            <p><b>Query:</b> <span style='font-size: 18px; color: #2c3e50;'>{row['query']}</span></p>
            <p><b>Original Amazon Label:</b> <span style='color: red; font-weight: bold; font-size: 16px;'>{amazon_label}</span></p>
            <hr>
            <p><b>Product Title:</b> {title}</p>
            <p><b>Brand:</b> {brand} | <b>Color:</b> {color}</p>
            <p><b>Bullet Points:</b> {bullets_html}</p>
            <p><b>Description:</b> {desc_html}</p>
        </div>
        """
        
        with self.output_area:
            clear_output(wait=True)
            display(HTML(html_content))
            
        self.notes_box.value = ''

    def _handle_submit(self, b):
        """Saves the selected result and moves to the next item."""
        selected_option = self.label_dropdown.value
        
        if selected_option != 'Skip':
            # Extract just the single letter (E, S, C, or I) from the dropdown string
            label = selected_option.split(' ')[0]
            
            row = self.df.iloc[self.current_index]
            new_row = pd.DataFrame([{
                'example_id': row['example_id'],
                'query': row['query'],
                'original_label': row['esci_label'],
                'human_label': label,
                'human_notes': self.notes_box.value
            }])
            
            self.results_df = pd.concat([self.results_df, new_row], ignore_index=True)
            
            # Ensure parent directory exists before saving
            self.output_csv.parent.mkdir(parents=True, exist_ok=True)
            self.results_df.to_csv(self.output_csv, index=False)
            
        self.current_index += 1
        self._show_current()
