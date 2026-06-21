import pytest
import pandas as pd
from src.ingestion.options_streamer import OptionsStreamer

def test_parse_option_chain_payload():
    streamer = OptionsStreamer(client=None)

    payload_safe = [
        {"StrikeRate": 23500, "CPType": "CE", "OpenInterest": 100, "Volume": 50, "LastRate": 10.5},
        {"StrikeRate": 24000, "CPType": "PE", "OpenInterest": 200, "Volume": 150, "LastRate": 20.5}
    ]

    df = streamer.parse_option_chain_payload(payload_safe, None)
    assert not df.empty
    assert len(df) == 2

    # Since it groups by strike, 23500 CE is one row
    row0 = df[df['strike_price'] == 23500].iloc[0]
    assert row0['call_oi'] == 100
    assert row0['put_oi'] == 0
    assert row0['ce_premium'] == 10.5
    assert row0['pe_premium'] == 0.0

    # 24000 PE is another row
    row1 = df[df['strike_price'] == 24000].iloc[0]
    assert row1['call_oi'] == 0
    assert row1['put_oi'] == 200
    assert row1['ce_premium'] == 0.0
    assert row1['pe_premium'] == 20.5
