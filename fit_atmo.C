
#include <iostream>
#include <vector>
#include <math.h>

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

    // Load atmosphere csv
    auto par = ROOT::RDF::FromCSV("data/AtmoUSStd.csv");

    // std::cout << par.Describe() << std::endl;


    for (int H = 0; H < 100; H += 10) {
        // std::cout << H << " km:" << calculate_density(H, model_USStd) << std::endl;
    }

    auto par2 = par.Define("dens_USStd", [&model_USStd](double H) { return calculate_density(H, model_USStd); }, {"altitude"});
    par2 = par2.Define("dens_Linsley", [&model_Linsley](double H) { return calculate_density(H, model_Linsley); }, {"altitude"});
    par2 = par2.Define("dens_scipyFit", [&model_scipyFit](double H) { return calculate_density(H, model_scipyFit); }, {"altitude"});

    par2 = par2.Define("ratio_USStd", "dens_USStd / density");
    par2 = par2.Define("ratio_Linsley", "dens_Linsley / density");
    par2 = par2.Define("ratio_scipyFit", "dens_scipyFit / density");

    // par2.Display("")->Print();

    auto canvas = new TCanvas("c", "c", 1600, 1200);

    auto h_ref = par2.Graph("altitude", "density");
    auto h_USStd = par2.Graph("altitude", "ratio_USStd");
    auto h_Linsley = par2.Graph("altitude", "ratio_Linsley");
    auto h_scipyFit = par2.Graph("altitude", "ratio_scipyFit");

    auto fit_func = new TF1("expo_fit", "[0]/[1] * exp(-x*100000/[1])*1000", 0, 10);
    fit_func->SetParameter(0, 1000);
    fit_func->SetParameter(1, 600000);
    fit_func->SetLineColor(kGreen);
    h_ref->Fit(fit_func, "R");

    h_ref->SetLineColor(kRed+1);
    h_USStd->SetLineColor(kAzure-5);
    h_Linsley->SetLineColor(kOrange-3);
    h_scipyFit->SetLineColor(kGreen+2);
    h_ref->SetLineWidth(3);
    h_USStd->SetLineWidth(3);
    h_Linsley->SetLineWidth(3);
    h_scipyFit->SetLineWidth(3);

    // auto marker_style = 20;
    // h_ref->SetMarkerStyle(marker_style);
    // h_USStd->SetMarkerStyle(marker_style);
    // h_Linsley->SetMarkerStyle(marker_style);
    // h_scipyFit->SetMarkerStyle(marker_style);
    auto marker_size = 100.0;
    h_ref->SetMarkerStyle(marker_size);
    h_USStd->SetMarkerStyle(marker_size);
    h_Linsley->SetMarkerStyle(marker_size);
    h_scipyFit->SetMarkerStyle(marker_size);
    h_ref->SetMarkerColor(kRed+1);
    h_USStd->SetMarkerColor(kAzure-5);
    h_Linsley->SetMarkerColor(kOrange-3);
    h_scipyFit->SetMarkerColor(kGreen+2);

    // h_ref->Draw();
    h_USStd->Draw("al");
    h_Linsley->Draw("l,same");
    h_scipyFit->Draw("l,same");

    gPad->SetGrid(1,1);
    gPad->SetLogy();

    h_USStd->GetXaxis()->SetRangeUser(-1, 110);
    h_USStd->GetYaxis()->SetRangeUser(0.5, 2.4);
    canvas->SaveAs("plots/atmo_fit/root_density.pdf");

// # Axis ranges for altitude ranges
// x_limits = [[-1,20], [20,60], [60,110]]
// y_main_limits = [[0.08, 1.4], [0.0002, 0.095], [8e-8, 0.00035]]
// y_ratio_limits = [[0.982, 1.035], [0.82, 1.07], [0.5, 5]]

    h_USStd->GetXaxis()->SetRangeUser(-1, 20);
    h_USStd->GetYaxis()->SetRangeUser(0.982, 1.035);
    canvas->SaveAs("plots/atmo_fit/root_density_1.pdf");


    h_USStd->GetXaxis()->SetRangeUser(20, 60);
    h_USStd->GetYaxis()->SetRangeUser(0.82, 1.07);
    canvas->SaveAs("plots/atmo_fit/root_density_2.pdf");


    h_USStd->GetXaxis()->SetRangeUser(60, 110);
    h_USStd->GetYaxis()->SetRangeUser(0.5, 5);
    canvas->SaveAs("plots/atmo_fit/root_density_3.pdf");
    // std::cout
    // # Empty array for fit model
    // model_fit = []

    // # Fit boundaries
    // bounds = [-1, 3, 7, 11, 16, 22, 28, 35, 40, 45, 50, 61, 86, 110]

    

    return 0;

}