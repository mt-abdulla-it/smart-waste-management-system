def check_bin_levels(bins_data, threshold=80):
    """
    Checks which bins have exceeded the fill threshold.
    Returns a list of bin IDs that need immediate collection.
    """
    full_bins = []
    for bin_info in bins_data:
        if bin_info.get('fill_level', 0) >= threshold:
            full_bins.append(bin_info)
    return full_bins
