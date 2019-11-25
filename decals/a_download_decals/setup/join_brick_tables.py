import astropy.table


def merge_bricks_catalogs(coordinate_catalog, exposure_catalog, test_mode=False):
    """
    DR3+ puts brick coordinate edges and brick exposure counts in different tables (sad face).
    These tables need to be merged so that bricks with both good exposures and NSA galaxies can be identified
    Will only match bricks that have exactly the same name, ra and dec

    Args:
        coordinate_catalog (astopy.Table): table with ra/dec edges of all bricks
        exposure_catalog (astropy.Table) table with exposure counts of all bricks
        test_mode (bool): if True, override the assert sanity checks for unit testing of edge cases

    Returns:
        None
    """

    # coordinate catalog has brick listing for whole survey - more bricks than have been imaged in DR3
    if not test_mode:
        assert len(coordinate_catalog) > len(exposure_catalog)

    # Coordinate catalog has uppercase column names. Rename to lowercase match exposure_catalog.
    for colname in coordinate_catalog.colnames:
        coordinate_catalog.rename_column(colname, colname.lower())

    # merge on brickname
    assert len(coordinate_catalog['brickname']) == len(set(coordinate_catalog['brickname']))  # names must be unique
    bricks_catalog = astropy.table.join(
        coordinate_catalog,
        exposure_catalog,
        keys='brickname',  # also works with [brickname, ra, dec] but this avoids rounding errors
        join_type='inner')

    # check that all exposed bricks were 1-1 matched
    if not test_mode:  # avoid this check with some unit tests
        assert len(bricks_catalog) == len(exposure_catalog)

    return bricks_catalog

#     TODO move to settings file
#         brick_coordinates_loc (str): absolute file path to fits table of coordinates of all bricks
#         brick_exposures_loc (str):  absolute file path to fits table of coordinates of imaged bricks with exposure counts
#         brick_loc (str): absolute file path to save fits table of brick coordinates with exposure counts
