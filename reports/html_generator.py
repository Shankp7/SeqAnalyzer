import os
from datetime import datetime
import plotly.graph_objects as go

class HTMLReportGenerator:
    def generate_html_report(self, data, researcher_name, researcher_id, save_path):
        # Generate the interactive Plotly pie chart
        filtered_data = {k: v for k, v in data['counts'].items() if v > 0}
        labels = list(filtered_data.keys())
        values = list(filtered_data.values())
        
        color_map = {'A': '#ff9999', 'T': '#66b3ff', 'G': '#99ff99', 'C': '#ffcc99'}
        colors = [color_map.get(label, '#cccccc') for label in labels]

        fig = go.Figure(data=[go.Pie(labels=labels, values=values, marker=dict(colors=colors))])
        fig.update_traces(textposition='inside', textinfo='percent+label', hoverinfo='label+percent+value')
        fig.update_layout(
            title_text='Nucleotide Distribution',
            title_x=0.5,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        
        # Get chart HTML div (no full html wrapper, just the div)
        chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

        # Format restriction enzymes
        enzymes_html = ""
        for enz, sites in data['sites'].items():
            site_str = ", ".join(map(str, sites)) if sites else "None"
            enzymes_html += f"<li><strong>{enz}:</strong> {site_str}</li>"
            
        protein_display = data['protein'][:500] + "..." if len(data['protein']) > 500 else data['protein']

        # HTML Template
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SeqAnalyzer Interactive Report - {data['id']}</title>
            <style>
                body {{
                    background-color: #1e1e1e;
                    color: #e0e0e0;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    max-width: 1000px;
                    margin: auto;
                    background-color: #2b2b2b;
                    padding: 30px;
                    border-radius: 12px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.5);
                }}
                h1 {{
                    color: #2ecc71;
                    text-align: center;
                    border-bottom: 2px solid #2ecc71;
                    padding-bottom: 10px;
                }}
                .header-info {{
                    display: flex;
                    justify-content: space-between;
                    color: #aaaaaa;
                    font-size: 0.9em;
                    margin-bottom: 20px;
                }}
                .grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                }}
                .card {{
                    background-color: #383838;
                    padding: 20px;
                    border-radius: 8px;
                }}
                h3 {{
                    color: #f1c40f;
                    margin-top: 0;
                }}
                .metric-row {{
                    display: flex;
                    justify-content: space-between;
                    border-bottom: 1px solid #555;
                    padding: 8px 0;
                }}
                .metric-value {{
                    font-weight: bold;
                    color: #fff;
                }}
                .chart-container {{
                    grid-column: 1 / -1;
                    background-color: #383838;
                    border-radius: 8px;
                    padding: 10px;
                    display: flex;
                    justify-content: center;
                }}
                .protein-seq {{
                    font-family: 'Courier New', Courier, monospace;
                    word-wrap: break-word;
                    background-color: #111;
                    padding: 15px;
                    border-radius: 5px;
                    font-size: 0.9em;
                }}
                ul {{
                    list-style-type: none;
                    padding: 0;
                }}
                li {{
                    padding: 5px 0;
                    border-bottom: 1px solid #444;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>SeqAnalyzer: Genomic Bio-Intelligence Report</h1>
                
                <div class="header-info">
                    <div>
                        <strong>Researcher:</strong> {researcher_name}<br>
                        {f"<strong>ID:</strong> {researcher_id}" if researcher_id else ""}
                    </div>
                    <div>
                        <strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    </div>
                </div>

                <div class="grid">
                    <div class="card">
                        <h3>Primary Metrics</h3>
                        <div class="metric-row"><span>Sequence ID:</span> <span class="metric-value">{data['id']}</span></div>
                        <div class="metric-row"><span>Total Length:</span> <span class="metric-value">{data['length']} bp</span></div>
                        <div class="metric-row"><span>Molecular Weight:</span> <span class="metric-value">{data['weight']:.2f} Da</span></div>
                        <div class="metric-row"><span>GC Content:</span> <span class="metric-value">{data['gc']:.2f}% ({data['stability']})</span></div>
                        <div class="metric-row"><span>Shannon Entropy:</span> <span class="metric-value">{data['entropy']:.4f}</span></div>
                        <div class="metric-row"><span>Invalid Bases:</span> <span class="metric-value">{data['invalid']}</span></div>
                    </div>

                    <div class="card">
                        <h3>Thermal Properties</h3>
                        <div class="metric-row"><span>Tm (Wallace):</span> <span class="metric-value">{data['tm_w']:.2f} &deg;C</span></div>
                        <div class="metric-row"><span>Tm (Salt-Adjusted):</span> <span class="metric-value">{data['tm_s']:.2f} &deg;C</span></div>
                    </div>

                    <div class="chart-container">
                        {chart_html}
                    </div>

                    <div class="card">
                        <h3>Restriction Enzyme Mapping</h3>
                        <ul>
                            {enzymes_html}
                        </ul>
                    </div>

                    <div class="card">
                        <h3>Protein Translation (First 200 aa)</h3>
                        <div class="protein-seq">{protein_display}</div>
                    </div>
                </div>
                
                <p style="text-align: center; margin-top: 30px; font-size: 0.8em; color: #777;">
                    Generated by SeqAnalyzer Interactive HTML Engine
                </p>
            </div>
        </body>
        </html>
        """

        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return True
