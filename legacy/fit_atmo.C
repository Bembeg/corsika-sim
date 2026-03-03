
#include <iostream>
#include <string>
#include <vector>
#include <math.h>
#include <map>

#include <TF1.h>
#include <TCanvas.h>

double calculate_density(double H, std::vector<std::vector<double>>& model) {
    auto offset = model.at(size(model)-1).at(1);
    auto scale = model.at(size(model)-1).at(2);
    for (const auto& set : model) {
        if (H < set.at(0)) {
            offset = set.at(1);
            scale = set.at(2);
            break;
        }
    }

    return offset/scale * exp(-(H)*100000/scale); 
}

int fit_atmo() {
    // Load atmosphere csv
    auto par = ROOT::RDF::FromCSV("data/CTA_N.csv");

    // Histogram of tabulated density
    auto h_ref = par.Graph("altitude", "density");

    // Fit boundaries
    std::vector<std::pair<int,int>> bounds = {
        {-1,3}, {3,7}, {7,11}, {11,16},
        {16,22}, {22,28}, {28,35}, {35,40},
        {45,50}, {50,60}, {60,70}, {70,80},
        {80,90}, {90,100}, {100,120}};

    std::vector<std::vector<double>> model_fit{};
    std::map<int, TF1*> fits{};

    // Make fits
    for (const auto& b : bounds) {
        auto x_lo = b.first;
        auto x_hi = b.second;
        TString fit_name = "expoFit" + std::to_string(x_hi);

        std::cout << "Fitting base range (" << x_lo << " - " << x_hi << "):" << std::endl;

        auto best_chi2 = 1e9;

        for (int sh_lo = 0; sh_lo <= 0; sh_lo++) {
            for (int sh_hi = 0; sh_hi <= 0; sh_hi++) {
                for (double of_sh = -10; of_sh <= 10; of_sh++) {  
                    for (double sc_sh = -10; sc_sh <= 10; sc_sh++) {  
                        auto mod_x_lo = x_lo + sh_lo * static_cast<double>(x_hi-x_lo)/5;
                        auto mod_x_hi = x_hi + sh_hi * static_cast<double>(x_hi-x_lo)/5;
                        // std::cout << "  - current range (" << mod_x_lo << " - " << mod_x_hi << "): ";

                        auto fit = new TF1(fit_name, "[0]/[1] * exp(-x*100000/[1])", mod_x_lo, mod_x_hi);
                        fit->SetParameter(0, 700 + 50*of_sh);
                        fit->SetParLimits(0, 100, 1700);
                        fit->SetParameter(1, 7e5 + 5e4*sc_sh);
                        fit->SetParLimits(1, 1e5, 1.5e6);
                        h_ref->Fit(fit, "RNQ");
                        
                        auto chi2_ndf = fit->GetChisquare()/fit->GetNDF();
                        // std::cout << "chi2/NDF=" << chi2_ndf << std::endl;
                        if (chi2_ndf < best_chi2) {
                            // std::cout << "    best fit so far" << std::endl;
                            fits[x_hi] = fit;
                            best_chi2 = chi2_ndf;
                        }   
                    }
                }
            }
        }
        
        double ran_x, ran_y;
        fits.at(x_hi)->GetRange(ran_x, ran_y);

        std::cout << "Best fit for nominal range (" << x_lo << "-" << x_hi
         << "): range=(" << ran_x << "-" << ran_y << "), offset=" << fits.at(x_hi)->GetParameter(0) << ", scale=" << fits.at(x_hi)->GetParameter(1) << std::endl;

        fits.at(x_hi)->SetLineColor(kGreen);
        h_ref->Fit(fits.at(x_hi), "RNQ");
        
        // Register best model
        model_fit.push_back({static_cast<double>(x_hi), fits.at(x_hi)->GetParameter(0), fits.at(x_hi)->GetParameter(1)});
    }

    // Add columns with fit density and fit/table ratio
    auto par2 = par.Define("dens_ROOTFit", [&model_fit](double H) { return calculate_density(H, model_fit); }, {"altitude"});
    par2 = par2.Define("ratio_ROOTFit", "dens_ROOTFit / density");

    // Fit density and ratio graphs
    auto h_ROOTFit = par2.Graph("altitude", "dens_ROOTFit");
    auto hR_ROOTFit = par2.Graph("altitude", "ratio_ROOTFit");

    // Draw options
    h_ref->SetLineColor(kBlack);
    h_ROOTFit->SetLineColor(kRed+1);
    hR_ROOTFit->SetLineColor(kRed+1);
    h_ref->SetMarkerColor(kBlack);
    h_ROOTFit->SetMarkerColor(kRed+1);
    hR_ROOTFit->SetMarkerColor(kRed+1);
    auto line_width = 2;
    h_ref->SetLineWidth(line_width);
    h_ROOTFit->SetLineWidth(line_width);
    hR_ROOTFit->SetLineWidth(line_width);
    auto marker_style = 20;
    h_ref->SetMarkerStyle(marker_style);
    h_ROOTFit->SetMarkerStyle(marker_style);
    hR_ROOTFit->SetMarkerStyle(marker_style);
    auto marker_size = 1.5;
    h_ref->SetMarkerSize(marker_size);
    h_ROOTFit->SetMarkerSize(marker_size);
    hR_ROOTFit->SetMarkerSize(marker_size);
    auto size = 0.06;
    h_ref->GetYaxis()->SetLabelSize(size);
    h_ref->GetYaxis()->SetTitleSize(size);
    hR_ROOTFit->GetXaxis()->SetLabelSize(size);
    hR_ROOTFit->GetXaxis()->SetTitleSize(size);
    hR_ROOTFit->GetYaxis()->SetLabelSize(size);
    hR_ROOTFit->GetYaxis()->SetTitleSize(size);
    // Title and axis labels
    h_ref->SetTitle(";;#rho [g/cm^{3}]");
    hR_ROOTFit->SetTitle(";H [km];#rho_{fit} / #rho_{tab}");
    // Axis divisions
    h_ref->GetYaxis()->SetNdivisions(8);
    hR_ROOTFit->GetYaxis()->SetNdivisions(8);

    // Canvas
    auto canvas = new TCanvas("c", "c", 1200, 800);
    canvas->SetRightMargin(0);
    canvas->SetTopMargin(0);
    gStyle->SetGridColor(15);
    gPad->SetGrid(1,1);
    // Divide canvas
    canvas->Divide(1, 2, 0, 0);
    
    // Upper pad
    canvas->cd(1);
    gPad->SetGrid(1,1);
    gPad->SetRightMargin(0.05);
    gPad->SetTopMargin(0.15);
    gPad->SetLogy(1);

    // Draw density
    h_ref->Draw("apl");
    h_ROOTFit->Draw("l,same");

    // Lower pad
    canvas->cd(2);
    gPad->SetGrid(1,1);
    gPad->SetRightMargin(0.05);
    gPad->SetBottomMargin(0.15);
    
    // Draw density ratio
    hR_ROOTFit->Draw("apl");
 
    std::vector<std::pair<int, int>> plot_bounds = {{0,120}, {1,20}, {20,60}, {60,120}};

    for (int n = 0; n < plot_bounds.size(); n++) {
        auto x_lo = plot_bounds.at(n).first;
        auto x_hi = plot_bounds.at(n).second;

        auto par_filt = par2.Filter([&x_lo, &x_hi](double alt){ return (alt >= x_lo) && (alt <= x_hi); }, {"altitude"});
        auto yR_max = par_filt.Max("ratio_ROOTFit").GetValue();
        auto yR_min = par_filt.Min("ratio_ROOTFit").GetValue();
        auto y_max = std::max(par_filt.Max("dens_ROOTFit").GetValue(), par_filt.Max("density").GetValue());
        auto y_min = std::min(par_filt.Min("dens_ROOTFit").GetValue(), par_filt.Min("density").GetValue());

        h_ref->GetXaxis()->SetLimits(x_lo, x_hi);
        h_ref->GetYaxis()->SetRangeUser(y_min*0.995, y_max*1.005);
        hR_ROOTFit->GetXaxis()->SetLimits(x_lo, x_hi);
        hR_ROOTFit->GetYaxis()->SetRangeUser(yR_min*0.995, yR_max*1.005);
        
        canvas->SaveAs(TString("plots/atmo_fit/root_density_" + std::to_string(n) + ".pdf"));
    }

    return 0;
}