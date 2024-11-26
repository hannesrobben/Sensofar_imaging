
def get_structure_data(dataframe: pd.DataFrame, line_axis: str = "y") -> (np.array, np.array):
    """
    used for sensofar system without removing background
    :param dataframe:
    :param line_axis:
    :return:
    lines with structures -> returns a np. array only with the lines containing the structure
    y_val -> returns a np.array which contains information of the corresponding y data
    """
    if not line_axis.lower() == "y":
        raise NotImplementedError(f"No method for axis {line_axis} implemented.")
    # ToDO: y_val usw. alles möglich machen, damit man die linien auch bei der x achse bekommt - dementsprechend auch namen ändern
    # variable declaration
    start = True
    lines = []
    y_val = []
    index_start = 0
    index_end = 0
    # ToDo: alles in dataframes umsetzen und nicht hier in sowas
    # getting values and start and end index
    for line_id, line_data in dataframe.groupby('line_y'):
        # Ensure line_data is sorted by some coordinate if needed
        line_points = line_data[['x', 'z']].values
        lines.append(line_points)
        a = line_data['y'].drop_duplicates().values
        y_val.append(a)

        z_mean = np.array(lines[line_id], dtype=object).mean(axis=0)[1]  # mean of z value of line
        # ToDo: schöner implementierung für das herausfinden der indices
        if z_mean >= 1:
            if start:
                start = False
                index_start = line_id
            index_end = line_id  #

    y_val = y_val[index_start:index_end]
    lines_w_structure = lines[index_start:index_end]
    # mid_line = np.array(lines[np.ceil((index_start + index_end) / 2).astype(int)]).transpose()
    return np.array(lines_w_structure).transpose(), np.array(y_val)


def read_dat_file_to_dataframe(file_path):
    """
    Liest eine .dat Datei ein und gibt den Inhalt als Pandas DataFrame zurück.

    :param file_path: Der Pfad zur .dat Datei
    :return: Ein Pandas DataFrame mit dem Inhalt der Datei
    """
    try:
        # Lesen der Datei mit Pandas, Annahme dass die Datei durch Semikolons getrennt ist
        df = pd.read_csv(file_path, delimiter=';', header=None, names=['x', 'y', 'z'])

        # Erkennen der Linienanfänge
        start_value = df['x'].iloc[0]  # Annahme: die Linie beginnt immer mit demselben x-Wert
        df['line_y'] = (df['x'] == start_value).cumsum() - 1
        return df

    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
        return None



# old code for comparison the lenses 29.07


def plot_y_dir_complete_in_2Plots(path):
    # das ist einfach eine ausgelagerte funktion,die zum testen und zur Visualisierung genutzt wurde.
    # Nimmt den data_path und erzeugt zwei graphen, die den Verlauf in y-richtung zeigen
    # rot ist die mittlere ebene und blau sind alle weiteren datenpunkt
    # erster graph ist von start der struktur +10 bis mitte, zweite von mitte bis ende (umgekehrt in for schleife wegen roter Linie)

    data_aspherical_left = SensofarData(path)
    px_size = data_aspherical_left.pixel_size

    mid_point = data_aspherical_left.structure_loc_mid[0]  # 1362 1046
    start_pnt = data_aspherical_left.structure_loc[0][0]
    end_pnt = data_aspherical_left.structure_loc[1][0]

    x_0 = data_aspherical_left.structure_loc_mid[1]
    x_0_re = x_0 * px_size

    for i in range(mid_point - start_pnt):
        if i < 10: continue
        point = start_pnt + i
        data = data_aspherical_left.get_y_profile(index=point)
        n_data_pnts = len(data)
        x_arr = np.arange(0, n_data_pnts * px_size, px_size)
        # x_arr = x_arr - x_arr[mid_point]
        if point == mid_point - 1:
            plt.plot(x_arr, data, color="red")
            plt.plot(x_0_re, data[x_0], "go")
        else:
            plt.plot(x_arr, data, color="blue")

    fig = plt.figure()
    for i in range(end_pnt - mid_point):
        if i < 10: continue
        point = end_pnt - i
        data = data_aspherical_left.get_y_profile(index=point)
        n_data_pnts = len(data)
        x_arr = np.arange(0, n_data_pnts * px_size, px_size)
        # x_arr = x_arr - x_arr[mid_point]
        if point == mid_point + 1:
            plt.plot(x_arr, data, color="red")
            plt.plot(x_0_re, data[x_0], "go")
        else:
            plt.plot(x_arr, data, color="blue")


def old_saving_fig():
    base_path = 'C:\\Users\\hanne\\Documents\\Seafile\\Nanoproduction_Hannes\\Sensofar'
    experiment = "2024_06_25 DHM Paper Pillow test\Data"
    path = os.path.join(base_path, experiment)

    data_name = "Aspherical_left_good.dat"
    data_path = os.path.join(base_path, experiment, data_name)

    # ------------------------------------------------------------------------------------------------------------------
    # ======  Plot Aspherical lens   ======
    # ------------------------------------------------------------------------------------------------------------------

    data_aspherical_left = SensofarData(data_path)
    px_size = data_aspherical_left.pixel_size
    mid_point = data_aspherical_left.structure_loc_mid

    fig = plt.figure(dpi=400)

    data = data_aspherical_left.get_y_profile(index=mid_point[0])
    n_data_pnts = len(data)
    x_arr = np.arange(0, n_data_pnts * px_size, px_size)
    x_arr = x_arr - x_arr[mid_point[1]]  # verschiebung zurm 0-Punkt
    plt.plot(x_arr, data)

    # ------------------------------------------------------------------------------------------------------------------
    # ======  Plot Comparison   ======
    # ------------------------------------------------------------------------------------------------------------------

    height = 7
    length = 100
    width = 75
    lens = AsphericalLens((0, 0, 0), height=height, length=length, width=width, radius_of_curvature=2030,
                          slice_size=.1, conic_constant_k=-2.3, alpha=0, hatch_size=0.1, velocity=40000)
    # Plot the calculation
    prof, hei = lens.calc_profile(axis='y', pos=0, step_size=px_size)
    prof = np.array(prof)
    hei = -1 * np.array(hei) + lens.height
    plt.plot(prof, hei, color="orange")

    # ------------------------------------------------------------------------------------------------------------------
    # ======  Save Figure   ======
    # ------------------------------------------------------------------------------------------------------------------
    data_name_list = ["test", "test1"]
    i = 0
    fig_name = f"Comparison of {data_name_list[i]} and specified lens"
    save_path = os.path.join(path, fig_name)
    fig.savefig(save_path)



