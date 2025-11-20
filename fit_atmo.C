
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

    return offset/scale * exp(-(H)*100000/scale)*1000; 
}

int fit_atmo() {
    // Two models from C7/C8
    std::vector<std::vector<double>> model_USStd = {
        {7, 1183.6071, 954248.34},
        {11.4, 1143.0425, 800005.34},
        {37, 1322.9748, 629568.93},
        {100, 655.67307, 737521.77}
    };

    std::vector<std::vector<double>> model_Linsley = {
        {4, 1222.6562, 994186.38},
        {10, 1144.9069, 878153.55},
        {40, 1305.5948, 636143.04},
        {100, 540.1778, 772170.16}
    };

    std::vector<std::vector<double>> model_scipyFit = {
        {3, 1242.8856, 1014510.54},
        {7, 1168.5962, 928445.41},
        {11, 1143.0824, 837817.65},
        {16, 1306.6105, 637130.11},
        {22, 1305.8958, 637199.08},
        {28, 1315.8478, 633553.13},
        {35, 1232.0029, 646640.96},
        {40, 1057.1476, 668578.95},
        {45, 845.4810, 700320.13},
        {50, 500.8463, 775301.57},
        {61, 333.2669, 839035.22},
        {86, 757.3471, 743155.35},
        {110, 700.0000, 700000.00},
    };

    std::vector<std::vector<double>> model_fit{};

    // Load atmosphere csv
    auto par = ROOT::RDF::FromCSV("data/AtmoUSStd.csv");

    auto par2 = par.Define("dens_USStd", [&model_USStd](double H) { return calculate_density(H, model_USStd); }, {"altitude"});
    par2 = par2.Define("dens_Linsley", [&model_Linsley](double H) { return calculate_density(H, model_Linsley); }, {"altitude"});
    par2 = par2.Define("dens_scipyFit", [&model_scipyFit](double H) { return calculate_density(H, model_scipyFit); }, {"altitude"});

    par2 = par2.Define("ratio_USStd", "dens_USStd / density");
    par2 = par2.Define("ratio_Linsley", "dens_Linsley / density");
    par2 = par2.Define("ratio_scipyFit", "dens_scipyFit / density");

    // Density graphs
    auto h_ref = par2.Graph("altitude", "density");


    // Fit boundaries
    std::vector<std::pair<int,int>> bounds = {
        {-1,3}, {3,7}, {7,11}, {11,16},
        {16,22}, {22,28}, {28,35}, {35,40},
        {45,50}, {50,61}, {61,70}, {70,80},
        {80,90}, {90,100}, {100,112}};

    // std::vector<std::pair<int,int>> bounds = {{-1,3}, {3,7}};


    std::map<int, TF1*> fits{};

    for (const auto& b : bounds) {
        auto x_lo = b.first;
        auto x_hi = b.second;
        TString fit_name = "expoFit" + std::to_string(x_hi);

        // std::cout << "Fitting base range (" << x_lo << " - " << x_hi << "):" << std::endl;

        auto best_chi2 = 1e9;

        for (int sh_lo = 0; sh_lo <= 0; sh_lo++) {
            for (int sh_hi = 0; sh_hi <= 0; sh_hi++) {
                for (double of_sh = -10; of_sh <= 10; of_sh++) {  
                    for (double sc_sh = -10; sc_sh <= 10; sc_sh++) {  
                        auto mod_x_lo = x_lo + sh_lo * static_cast<double>(x_hi-x_lo)/5;
                        auto mod_x_hi = x_hi + sh_hi * static_cast<double>(x_hi-x_lo)/5;
                        // std::cout << "  - current range (" << mod_x_lo << " - " << mod_x_hi << "): ";

                        auto fit = new TF1(fit_name, "[0]/[1] * exp(-x*100000/[1])*1000", mod_x_lo, mod_x_hi);
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
        // fits.at(x_hi)->Draw("same");
        h_ref->Fit(fits.at(x_hi), "RNQ");
        
        // std::cout << 

        // Register best model
        model_fit.push_back({static_cast<double>(x_hi), fits.at(x_hi)->GetParameter(0), fits.at(x_hi)->GetParameter(1)});
    }

    par2 = par2.Define("dens_ROOTFit", [&model_fit](double H) { return calculate_density(H, model_fit); }, {"altitude"});
    par2 = par2.Define("ratio_ROOTFit", "dens_ROOTFit / density");


    auto h_USStd = par2.Graph("altitude", "dens_USStd");
    auto h_Linsley = par2.Graph("altitude", "dens_Linsley");
    auto h_scipyFit = par2.Graph("altitude", "dens_scipyFit");
    auto h_ROOTFit = par2.Graph("altitude", "dens_ROOTFit");

    // Draw options
    h_ref->SetLineColor(kRed+1);
    h_USStd->SetLineColor(kAzure-5);
    h_Linsley->SetLineColor(kOrange-3);
    h_scipyFit->SetLineColor(kGreen+2);
    h_ROOTFit->SetLineColor(kBlack);
    h_ref->SetMarkerColor(kRed+1);
    h_USStd->SetMarkerColor(kAzure-5);
    h_Linsley->SetMarkerColor(kOrange-3);
    h_scipyFit->SetMarkerColor(kGreen+2);
    h_ROOTFit->SetMarkerColor(kBlack);
    auto line_width = 3;
    h_ref->SetLineWidth(line_width);
    h_USStd->SetLineWidth(line_width);
    h_Linsley->SetLineWidth(line_width);
    h_scipyFit->SetLineWidth(line_width);
    h_ROOTFit->SetLineWidth(line_width);
    auto marker_style = 20;
    h_ref->SetMarkerStyle(marker_style);
    h_USStd->SetMarkerStyle(marker_style);
    h_Linsley->SetMarkerStyle(marker_style);
    h_scipyFit->SetMarkerStyle(marker_style);
    h_ROOTFit->SetMarkerStyle(marker_style);
    auto marker_size = 1.5;
    h_ref->SetMarkerSize(marker_size);
    h_USStd->SetMarkerSize(marker_size);
    h_Linsley->SetMarkerSize(marker_size);
    h_scipyFit->SetMarkerSize(marker_size);
    h_ROOTFit->SetMarkerSize(marker_size);
    h_USStd->SetTitle("Luleo");

    // Density ratio to ref graphs
    auto hR_USStd = par2.Graph("altitude", "ratio_USStd");
    auto hR_Linsley = par2.Graph("altitude", "ratio_Linsley");
    auto hR_scipyFit = par2.Graph("altitude", "ratio_scipyFit");
    auto hR_ROOTFit = par2.Graph("altitude", "ratio_ROOTFit");
    // Draw options
    hR_USStd->SetLineColor(kAzure-5);
    hR_Linsley->SetLineColor(kOrange-3);
    hR_scipyFit->SetLineColor(kGreen+2);
    hR_ROOTFit->SetLineColor(kBlack);
    hR_USStd->SetMarkerColor(kAzure-5);
    hR_Linsley->SetMarkerColor(kOrange-3);
    hR_scipyFit->SetMarkerColor(kGreen+2);
    hR_ROOTFit->SetMarkerColor(kBlack);
    hR_USStd->SetLineWidth(line_width);
    hR_Linsley->SetLineWidth(line_width);
    hR_scipyFit->SetLineWidth(line_width);
    hR_ROOTFit->SetLineWidth(line_width);
    hR_USStd->SetMarkerStyle(marker_style);
    hR_Linsley->SetMarkerStyle(marker_style);
    hR_scipyFit->SetMarkerStyle(marker_style);
    hR_ROOTFit->SetMarkerStyle(marker_style);
    hR_USStd->SetMarkerSize(marker_size);
    hR_Linsley->SetMarkerSize(marker_size);
    hR_scipyFit->SetMarkerSize(marker_size);
    hR_ROOTFit->SetMarkerSize(marker_size);
    hR_USStd->SetTitle("");

    auto canvas = new TCanvas("c", "c", 1400, 1200);
    canvas->SetRightMargin(0);

    canvas->Divide(1, 2, 0, 0);
    canvas->cd(1);
    gPad->SetGrid(1,1);
    gPad->SetLogy();
    gPad->SetRightMargin(0.05);
    gPad->SetTopMargin(0.10);

    h_USStd->Draw("apl");
    h_Linsley->Draw("pl,same");
    h_scipyFit->Draw("pl,same");
    h_ref->Draw("pl,same");
    h_ROOTFit->Draw("pl,same");

    canvas->cd(2);
    gPad->SetGrid(1,1);
    // gPad->SetLogy();
    gPad->SetRightMargin(0.05);
    gPad->SetBottomMargin(0.15);
    hR_USStd->Draw("apl");
    hR_Linsley->Draw("pl,same");
    hR_scipyFit->Draw("pl,same");
    hR_ROOTFit->Draw("pl,same");
    h_USStd->GetYaxis()->SetNdivisions(10);

    hR_USStd->GetYaxis()->SetNdivisions(10);

    canvas->cd(1);
    gPad->SetLogy(0);

    // for (int n = 0; n < bounds.size(); n++) {
    //     auto x_lo = bounds.at(n).first;
    //     auto x_hi = bounds.at(n).second;

    //     auto par_filt = par2.Filter([&x_lo, &x_hi](double alt){ return (alt >= x_lo) && (alt <= x_hi); }, {"altitude"});
    //     auto yR_max = std::max(par_filt.Max("ratio_USStd").GetValue(), std::max(
    //                         par_filt.Max("ratio_Linsley").GetValue(), std::max(
    //                         par_filt.Max("ratio_scipyFit").GetValue(),
    //                         par_filt.Max("ratio_ROOTFit").GetValue())));
    //     auto yR_min = std::min(par_filt.Min("ratio_USStd").GetValue(), std::min(
    //                         par_filt.Min("ratio_Linsley").GetValue(), std::min(
    //                         par_filt.Min("ratio_scipyFit").GetValue(),
    //                         par_filt.Min("ratio_ROOTFit").GetValue())));
    //     auto y_max = std::max(par_filt.Max("dens_USStd").GetValue(), std::max(
    //                         par_filt.Max("dens_Linsley").GetValue(), std::max(
    //                         par_filt.Max("dens_scipyFit").GetValue(),
    //                         par_filt.Max("dens_ROOTFit").GetValue())));
    //     auto y_min = std::min(par_filt.Min("dens_USStd").GetValue(), std::min(
    //                         par_filt.Min("dens_Linsley").GetValue(), std::min(
    //                         par_filt.Min("dens_scipyFit").GetValue(),
    //                         par_filt.Min("dens_ROOTFit").GetValue())));

    //     h_USStd->GetXaxis()->SetLimits(x_lo, x_hi);
    //     hR_USStd->GetXaxis()->SetLimits(x_lo, x_hi);
    //     hR_USStd->GetYaxis()->SetRangeUser(yR_min*0.995, yR_max*1.005);
    //     h_USStd->GetYaxis()->SetRangeUser(y_min*0.995, y_max*1.005);

    //     canvas->SaveAs(TString("plots/atmo_fit/root_density_fit_" + std::to_string(x_hi) + ".pdf"));
    // }

    h_USStd->GetXaxis()->SetLimits(-1, 110);
    h_USStd->GetYaxis()->SetRangeUser(5e-8, 1.5);
    hR_USStd->GetYaxis()->SetRangeUser(0.5, 2.4);
    hR_USStd->GetXaxis()->SetLimits(-1, 110);
    canvas->SaveAs("plots/atmo_fit/root_density.pdf");

    h_USStd->GetXaxis()->SetLimits(-1, 20);
    h_USStd->GetYaxis()->SetRangeUser(0.08, 1.4);
    hR_USStd->GetXaxis()->SetLimits(-1, 20);
    hR_USStd->GetYaxis()->SetRangeUser(0.982, 1.035);
    canvas->SaveAs("plots/atmo_fit/root_density_1.pdf");

    h_USStd->GetXaxis()->SetLimits(20, 60);
    h_USStd->GetYaxis()->SetRangeUser(0.0002, 0.095);
    hR_USStd->GetXaxis()->SetLimits(20, 60);
    hR_USStd->GetYaxis()->SetRangeUser(0.82, 1.07);
    canvas->SaveAs("plots/atmo_fit/root_density_2.pdf");

    h_USStd->GetXaxis()->SetLimits(60, 113);
    h_USStd->GetYaxis()->SetRangeUser(8e-10, 3.5e-4);
    hR_USStd->GetXaxis()->SetLimits(60, 113);
    hR_USStd->GetYaxis()->SetRangeUser(0.5, 5);
    canvas->SaveAs("plots/atmo_fit/root_density_3.pdf");


    return 0;
}