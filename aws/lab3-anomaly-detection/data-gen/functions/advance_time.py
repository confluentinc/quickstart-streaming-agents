from datetime import timedelta

def starting_timestamp(params):
    return params["args"]["startingTime"] - (1 * 24 * 60 * 60 * 1000)

def advance_time(params):
    state = params.get("state") or starting_timestamp(params)

    if (state < params["args"]["startingTime"]):
        return {
            "value": {
                "ts": int(state),
                "throttle": 0,
            },
            "state": state + params["args"]["historicalDelta"]
        }
    else:
        return {
            "value": {
                "ts": params["args"]["now"],
                "throttle": params["args"]["realtimeDelta"]
            },
            "state": state
        }