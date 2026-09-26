#include <iostream>

using namespace std;

string nombre, carrera;
float promedio, suma;

const int MAX_ALUMNOS = 10;
int TOT_ALUMNOS = 0;

int a, b;

class Materia {
    public:
    string nombre, clave;int creditos;

    Materia() {
        nombre = "Figma";
        clave = "0";
        creditos = 0;
    }

    void mostrarMateria(){
        cout<< "Materia: " << nombre;
    }

    string getClave() const {
        return clave;
    }
};

class Calificacion {
    public:
    string clave, periodo;float nota;

    Calificacion() {
        clave = "0";
        periodo = "2025-2026";
        nota = 0;
    }

        void mostrarCalificacion(){
        cout<< "Calificacion: " << nota;
    }
};

class Alumno  {
    private:
    string nombre;
    int edad;
    float promedio;
    Materia materias[10];
    Calificacion calificaciones[10];
    int numMaterias;
    int numCalificaciones; 

    public:
    Alumno() : numMaterias(0), numCalificaciones(0) {
        nombre = "SUPER EMILIA";
        edad = 1000;
        promedio = 9;
    }

    ~Alumno() {
        cout << "Has destruido al estudiante " << nombre << ", eres un monstruo\n";
    }

    void leerDatos() {
        cout << "Introduce el Nombre: ";
        cin >> nombre;
        cout << "Introduce la Edad: ";
        cin >> edad;
        cout << "Introduce el Promedio: ";
        cin >> promedio;
    }

    void mostrar(int indice) const {
            cout << "Estudiante: " <<  nombre << " Edad: " << edad << " Promedio: " << promedio << " Indice:" << indice << "\n";

    }

    void setNombre(string n) {
        nombre = n;
    }

    void setEdad(int e) {
        if (e >= 0) { // validación
        edad = e;
    }
    }

    void setPromedio(float e) {
        if (e >= 0) { // validación
        promedio = e;
    }
    }

    string getNombre() const {
        return nombre;
    }

    int getEdad() const {
        return edad;
    }

    int getPromedio() const {
        return edad;
    }

    int buscarMateria(string clave) {
    for (int i = 0; i < numMaterias; i++) {
        if (materias[i].getClave() == clave) {
        return i;}}
    return -1;}

    void agregarMateria(Materia m) {
    if (numMaterias < 10) {
        materias[numMaterias] = m;
        numMaterias++;}
    }

};

Alumno alumnos[MAX_ALUMNOS];



void registrarAlumnos(){
    alumnos[TOT_ALUMNOS].leerDatos();
    TOT_ALUMNOS++;
    cout << "Carga Finalizada\n";
}

void mostrarEstudiante(){
    int estudiante;

    cout<<"Introduce el indice de estudiante: MAX: "<< TOT_ALUMNOS-1 << ": ";
    cin >> estudiante;

    if (estudiante < TOT_ALUMNOS and estudiante >=0) {

        alumnos[estudiante].mostrar(estudiante);
        cout << "Alumno Mostrado\n";
    }
    else {cout<<"Error\n";}
}

void intercambiarEstudiante(){
    cout << "Introduce el indice del primer alumno\n"; 
    cin >> a;
    cout << "Introduce el indice del segundo alumno\n"; 
    cin >> b;

    cout <<"Se intercambiaran "<< a <<" con "<< b <<"\n";

    string nombre_temp;

    int edad_temp;
    double promedio_temp;
            
    nombre_temp=alumnos[a].getNombre();
    edad_temp=alumnos[a].getEdad();
    promedio_temp=alumnos[a].getPromedio();

    alumnos[a].setNombre(alumnos[b].getNombre());
    alumnos[a].setEdad(alumnos[b].getEdad());
    alumnos[a].setPromedio(alumnos[b].getPromedio());

    alumnos[b].setNombre(nombre_temp);
    alumnos[b].setEdad(edad_temp);
    alumnos[b].setPromedio(promedio_temp);

    cout << "Alumnos Intercambiados\n";
}

void buscarEstudiante(){
    string buscar;

    cout<<"Introduce el nombre de estudiante: ";
    cin >> buscar;

    int pos = -1;
    for (int i = 0; i < TOT_ALUMNOS; i++) 
    {
        if (alumnos[i].getNombre() == buscar) 
        {
            pos = i;
            break;
        }
    }
    if (pos != -1) 
    {
        alumnos[pos].mostrar(pos);       } 
    else 
    {
        cout << "no encontrado\n";
    }
}

void eliminarEstudiante(){
    int estudiante;

    cout<<"Introduce el indice de estudiante: MAX: "<< TOT_ALUMNOS-1 << ": ";
    cin >> estudiante;

    if (estudiante < TOT_ALUMNOS and estudiante >=0) {
        alumnos[estudiante].mostrar(estudiante);
        for (int i = estudiante; i < TOT_ALUMNOS - 1; i++) {
            alumnos[i].setNombre (alumnos[i+1].getNombre());
            alumnos[i].setEdad(alumnos[i+1].getEdad());
            alumnos[i].setPromedio (alumnos[i+1].getPromedio());
            }
            TOT_ALUMNOS--;
        cout << "Alumno Eliminado\n";
    }
    else {cout<<"Error\n";}
}

void modificarEstudiante(){
    int indiceEstudiante;

    cout<<"Introduce el indice de estudiante: MAX: "<< TOT_ALUMNOS-1 << ": ";
    cin >> indiceEstudiante;

    if (indiceEstudiante < TOT_ALUMNOS and indiceEstudiante >=0) {
        alumnos[indiceEstudiante].mostrar(indiceEstudiante);
        alumnos[indiceEstudiante].leerDatos();
        cout << "Alumno Modificado\n";
    }
    else {cout<<"Error\n";} 
}

void mostrarEstudiantes(){
    for (int i = 0; i < TOT_ALUMNOS; i++) {

        alumnos[i].mostrar(i);
    }
    cout << "Alumnos Finalizado\n";
}

void calcularPromedio(){
    suma = 0;
    for (int i = 0; i < TOT_ALUMNOS; i++) {
        suma = suma + alumnos[i].getPromedio();
    }

    promedio= (suma)/TOT_ALUMNOS;
    cout << "El promedio es: "<< promedio << "\n";  
}

int main() 
{


    alumnos[0].setNombre("Jorge");
    alumnos[0].setEdad(33);
    alumnos[0].setPromedio(90);
    TOT_ALUMNOS++;

    alumnos[1].setNombre("Oscar");
    alumnos[1].setEdad(95);
    alumnos[1].setPromedio(2000);
    TOT_ALUMNOS++;

    alumnos[2].setNombre("Helen");
    alumnos[2].setEdad(18);
    alumnos[2].setPromedio(1);
    TOT_ALUMNOS++;

    TOT_ALUMNOS=TOT_ALUMNOS+5;

    int opcion, edad;
    while (true)

    {
    
    cout << "===== MENU =====\n"; 
    cout << "1 Registrar Alumno\n"; 
    cout << "2 Mostrar Alumno\n";
    cout << "3 Intercambiar Alumno\n";
    cout << "4 Buscar Alumno\n";  
    cout << "5 Eliminar Alumno\n";
    cout << "6 Modificar Alumno\n";   
    cout << "7 Mostrar todos los alumnos\n"; 
    cout << "8 Calcular promedio\n";
    cout << "9 Salir\n"; 

    cin >> opcion;

    switch (opcion) {
        case 1:
            registrarAlumnos();
            break;

        case 2:
            mostrarEstudiante();
            break;

        case 3:
            intercambiarEstudiante();
            break;

        case 4:
            buscarEstudiante();
            break;

        case 5:
            eliminarEstudiante();
            break;

        case 6:
            modificarEstudiante();
            break;

        case 7:
            mostrarEstudiantes();
            break;

        case 8:
            calcularPromedio();
            break;
        
        case 9:
            cout << "Bye Bye\n";
            return 0;
            
    
        }
    }
    return 0;
}
