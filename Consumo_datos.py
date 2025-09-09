##Carga de librerias
import requests
import pandas as pd
import streamlit as st  

##Definición de API y parámetros

url = 'https://datos.gob.cl/api/3/action/datastore_search'
params={
    'resource_id':'843f906c-e67e-4b04-9063-055c7bba8a72'
}

response=requests.get(url, params=params)
##Conexión a la API y carga de datos en un DataFrame
if response.status_code == 200:
    print("Conexión exitosa")
    data = response.json()
    registros = data['result']['records']
    data = pd.DataFrame(registros)
    print(data)
else:
    print("Error en la conexión:", response.status_code)

#print(data.head())
#print(data.columns)

##Interfaz de usuario con Streamlit
st.title("Ejecución Presupuestaria del Gobierno de Chile 2024:")
st.write("Análisis de datos de ejecución presupuestaria según la Ley de Presupuestos del Sector Público de Chile.")


#Parse de datos a float
for col in ["Suma de Monto Identificado Ley de Pptos.","Suma de Monto Devengado Ley de Pptos."]:
    data[col]=pd.to_numeric(data[col].str.replace(".","",regex=False).astype(float),errors='coerce')

#Agrupación de datos por región
monto_asignado=data.groupby(["Nombre Region Destino"])["Suma de Monto Identificado Ley de Pptos."].sum(numeric_only=True).reset_index()
monto_devengado=data.groupby(["Nombre Region Destino"])["Suma de Monto Devengado Ley de Pptos."].sum(numeric_only=True).reset_index()



#Subtitulo 1
#Montos totales
st.subheader("Monto Totales Ley Ppto:")
suma_asignado=monto_asignado["Suma de Monto Identificado Ley de Pptos."].sum()
suma_devengado=monto_devengado["Suma de Monto Devengado Ley de Pptos."].sum()

df_totales=pd.DataFrame({
        "Concepto:":["Monto Asignado","Monto Devengado","Saldo Disponible"],
        "Monto $MM":[suma_asignado,suma_devengado,suma_devengado-suma_asignado]
})  
df_totales["Monto $MM"]=df_totales["Monto $MM"].apply(lambda x: f"${x:,.0f}".replace(",","."))
st.dataframe(df_totales)
ejecucion=(suma_devengado/suma_asignado)*100
st.write("Ejecución Presupuestaria Total")
st.progress(int(ejecucion))
st.write(f"{ejecucion:.2f}%")

#Subtitulo 2
st.subheader("Montos Por Región:")

#filtro por región
region_seleccionada=st.selectbox("Seleccione una región:",data["Nombre Region Destino"].unique())

#df comparativo
df_comparativo=pd.merge(monto_asignado, monto_devengado, on="Nombre Region Destino")
print(df_comparativo.columns.tolist())
df_comparativo["Diferencia"]=df_comparativo["Suma de Monto Devengado Ley de Pptos."]-df_comparativo["Suma de Monto Identificado Ley de Pptos."]
df_comparativo["Diferencia %"]=((df_comparativo["Suma de Monto Devengado Ley de Pptos."]/df_comparativo["Suma de Monto Identificado Ley de Pptos."])*100).round(1)

#Encabezado DataFrame por región
st.write("Comparativo Monto Asignado vs Devengado por Región:")

#DF por región seleccionada
df_region=df_comparativo[df_comparativo["Nombre Region Destino"]==region_seleccionada]
st.dataframe(df_region)

#DF para gráfico de barras
df_barras=pd.DataFrame({
    "Concepto":["Monto Asignado","Monto Devengado"],
    "Monto $MM":[
                  df_region["Suma de Monto Identificado Ley de Pptos."].values[0],
                  df_region["Suma de Monto Devengado Ley de Pptos."].values[0],
                ]
}).set_index("Concepto")

#Gráfico de barras
st.subheader("Gráfico Por Región:")
st.bar_chart(df_barras)



