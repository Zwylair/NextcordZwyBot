async def calculate_pp(party_popularities: dict, party: str, new_popularity: int | float) -> dict:
    if new_popularity > party_popularities[party]:
        every_party_pop_minus = new_popularity - party_popularities[party]
    else:
        every_party_pop_minus = party_popularities[party] - new_popularity

    every_party_pop_minus /= len(party_popularities.keys()) - 1
    print(every_party_pop_minus)

    new_pp = {}
    for k, v in party_popularities.items():
        va = v - every_party_pop_minus if new_popularity > party_popularities[party] else v + every_party_pop_minus
        new_pp |= {k: va}
    new_pp[party] = new_popularity

    all_pp = 0
    for i in party_popularities.values():
        all_pp += i
    
    if all_pp != 100:
        new_pp[party] += 100 - all_pp

    return new_pp
