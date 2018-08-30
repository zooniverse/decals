import pandas as pd
import matplotlib.pyplot as plt


def get_summary_stats(name, dr):
    print('\n{}'.format(name))
    print('entries: {}'.format(len(dr)))
    print('unique galaxies: {}'.format(len(dr['iauname'].unique())))
    plt.figure()
    dr['redshift'].hist()
    plt.xlabel('redshift')
    plt.ylabel('galaxy count')
    plt.title('decals {} galaxy zoo subjects redshift'.format(name))
    plt.savefig('subjects_{}_redshift.png'.format(name))

    low_z = dr[dr['redshift'] < 0.05]
    print('entries below z=0.05: {}'.format(len(low_z)))
    print('unique galaxies below z=0.05: {}'.format(len(low_z['iauname'].unique())))

    print()


def investigate():
    interesting_cols = ['data_release', 'iauname', 'redshift']
    df = pd.read_csv(
        '/data/galaxy_zoo/decals/catalogs/galaxy_zoo_decals_with_nsa_v1_0_0.csv',
        nrows=None,
        usecols=interesting_cols)

    dr1 = df[df['data_release'] == 'DR1']
    dr2 = df[df['data_release'] == 'DR2']

    get_summary_stats('dr1', dr1)
    get_summary_stats('dr2', dr2)
    get_summary_stats('all', df)


if __name__ == '__main__':
    investigate()
