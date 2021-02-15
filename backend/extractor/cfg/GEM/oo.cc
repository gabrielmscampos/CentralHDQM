[plot:PedestalNoise_Width_me+42]
metric = basic.StdDev()
relativePath = CSC/CSCOfflineMonitor/PedestalNoise/hStripPedMEp42
yTitle = Width of pedestal noise (ME+42)

[plot:NSegments_Avg]
metric = basic.Mean()
relativePath = GEM/GEMEfficiency/StandaloneMuon/Efficiency/eff_muon_eta_ge+11_even
yTitle = in


[plot:eff_muon_eta_ge+11_odd]
metric = basic.Mean()
relativePath = GEM/GEMEfficiency/StandaloneMuon/Efficiency/eff_muon_eta_ge+11_odd
yTitle = in

[plot:eff_muon_eta_ge-11_even]
metric = basic.Mean()
relativePath = GEM/GEMEfficiency/StandaloneMuon/Efficiency/eff_muon_eta_ge-11_even
yTitle = in


[plot:eff_muon_eta_ge-11_odd]
metric = basic.Mean()
relativePath = GEM/GEMEfficiency/StandaloneMuon/Efficiency/eff_muon_eta_ge-11_odd
yTitle = in

[plot:digi_det_ge+11]
metric = basic.Mean()
relativePath = GEM/GEMOfflineMonitor/Digi/digi_det_ge+11
yTitle = VFAT(in)

[plot:digi_det_ge-11]
metric = basic.Mean()
relativePath = GEM/GEMOfflineMonitor/Digi/digi_det_ge-11
yTitle = VFAT(in)

[plot:hit_det_ge-11]
metric = basic.Mean()
relativePath = GEM/GEMOfflineMonitor/RecHit/hit_det_ge-11
yTitle = in

[plot:hit_det_ge+11]
metric = basic.Mean()
relativePath = GEM/GEMOfflineMonitor/RecHit/hit_det_ge+11
yTitle = in
