from sim.vtile import VTile

if __name__=="__main__":
    ops=VTile().run_fp32_saturation(10000)
    assert ops==256
    projected=ops*160*2.56e9/1e12
    print(f"PASS issue model: {ops:.0f} FP32 ops/cycle/tile")
    print(f"Architectural peak projection only: {projected:.4f} TFLOP/s")
