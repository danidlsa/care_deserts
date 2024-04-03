import pandas as pd
import numpy as np

def adjustment_factor(gdf, beta, gamma, umbral_area, nombre_col_desierto, travel_time_col):
    """
    Ajusta el umbral para identificar desiertos de cuidado basándose en el área y la densidad poblacional.

    Parámetros:
    - gdf: geoDataFrame que contiene los datos de las manzanas. 
    - beta: Sensibilidad del ajuste basado en el área.
    - gamma: Sensibilidad del ajuste inversamente proporcional a la densidad poblacional.
    - umbral_area: percentil del area de la manzana a partir del cual se aplicará el ajuste 
    - nombre_col_desierto: Nombre de la nueva columna que indicará si es desierto de cuidado ajustado.
    - travel_time_col: nombre de la columna de tiempo de viaje hasta centro más cercano
    """
    
    # Copia del DataFrame para no modificar el original
    manzanas_merged = gdf.copy()

    # Calcular el umbral de área como el percentil Z del área de las manzanas
    A_threshold = manzanas_merged['area_manzana'].quantile(umbral_area)

    # Calcular el ajuste combinado basado en área y densidad poblacional
    manzanas_merged['combined_adjustment'] = manzanas_merged.apply(
        lambda row: beta * (np.log1p(row['area_manzana']) - np.log1p(A_threshold)) + gamma / np.log1p(row['densidad_pob'])
        if row['area_manzana'] > A_threshold else 0,
        axis=1
    )

    # Aplicar el ajuste combinado para calcular el nuevo umbral ajustado
    manzanas_merged['adjusted_threshold'] = 20 + manzanas_merged['combined_adjustment']

    # Determinar el estado de desierto de cuidado con el nuevo umbral ajustado
    manzanas_merged['desierto_2'] = (manzanas_merged[travel_time_col] > manzanas_merged['adjusted_threshold']).astype(int)
    manzanas_merged[nombre_col_desierto] = manzanas_merged['desierto_2'] * manzanas_merged['alta_demanda']

    return manzanas_merged


## Population density helper


def pop_density(gdf, projected_crs, tot_pob_col):
    """
    Devuelve gdf proyectado y con columna de area y de densidad poblacional calculada

    Parámetros:
    - gdf: geoDataFrame que contiene los datos de las manzanas. 
    - codigo EPSG apropiado para el área. Ejemplo: 'EPSG:24891' 
    - tot_pob_col: nombre de la columna del gdf que contiene la información de población por segmento
    """
    # Re-project to the chosen CRS
    gdf_projected = gdf.to_crs(projected_crs)

    #  Now you can safely calculate areas without getting incorrect results due to the Earth's curvature
    gdf_projected['area_manzana'] = gdf_projected.geometry.area

    # Calculo densidad poblacional

    gdf_projected['densidad_pob'] = gdf_projected[tot_pob_col] / (gdf_projected['area_manzana'] / 1e6)  # Density in people per sq km

    return gdf_projected

