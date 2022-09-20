from billiards.geometry import ComposedPath
from billiards.numeric_methods import find_zero
from math import sin, cos, pi, asin, acos

def func_to_find_roots(boundary: ComposedPath, phi0: float, theta0: float):
    ''' recebe a fronteira do bilhar e a condição inicial do bilhar

    A saida é uma função real cuja raiz é o próximo ponto da órbita
    '''
    
    x0, y0 = boundary.get_point(phi0, evaluate=True)
    tangent_x0, tangent_y0 = boundary.get_tangent(phi0, evaluate=True)

    def func(phi):
        x, y = boundary.get_point(phi, evaluate=True)
        tangent_x, tangent_y = boundary.get_tangent(phi, evaluate=True)

        r_x = x - x0
        r_y = y - y0
        # (v_x, v_y) é perpendicular ao raio saindo de (x0, y0) com inclinação theta0 com a tangente
        v_x = -(tangent_x0)*sin(theta0) - (tangent_y0)*cos(theta0)
        v_y = -(tangent_y0)*sin(theta0) + (tangent_x0)*cos(theta0)
        drx = tangent_x
        dry = tangent_y
        
        return r_x*v_x + r_y*v_y, drx*v_x + dry*v_y

    return func

def make_billiard_map(boundary: ComposedPath, factor =100, debug = False, method = "newton", **kwargs):
    '''curve é uma função do tipo
    s --> [ (x,y), (x',y')]
    curva(s)[0] = (x,y) é um np.array
    curva(s)[1] = (x',y') é um np.array

    periodo = dominio da parametrização
    factor = relacionado ao intervalo onde sera procurada a raiz

    **kwargs: pra passar pro método de Newton.
    So tem dois possíveis
    acc = 0.0000000000001
    max_iteracao = 100
    '''

    if "acc" not in kwargs:
        acc = 0.0000000000001
    else:
        acc = kwargs["acc"]
    if "max_iteracao" not in kwargs:
        max_iteracao = 100
    else:
        max_iteracao = kwargs["max_iteracao"]

    if boundary.periodic:
        periodo = boundary.lengthFloat
    else:
        raise Exception("Can't simulate on non-periodic boundary")

    def billiard_map(phi0, theta0):
        func = func_to_find_roots(boundary, phi0, theta0)


        if ((-acc  < theta0) and (theta0 < acc)):
            theta1 = 0
            phi1 = phi0
        if ((pi-acc < theta0) and (theta0 < pi + acc)):
            theta1 = pi
            phi1 = phi0
        else:
            phi1 = find_zero(
                func,
                phi0 + factor*acc,
                phi0 + periodo - factor*acc,
                acc = acc,
                max_iter=max_iteracao,
                method=method)

            phi1 = phi1 % periodo

            x_phi1, y_phi1 = boundary.get_point(phi1, evaluate=True)
            x_phi0, y_phi0 = boundary.get_point(phi0, evaluate=True)
            dx_phi1, dy_phi1 = boundary.get_tangent(phi1, evaluate=True)

            r_x = x_phi1 - x_phi0
            r_y = y_phi1 - y_phi0
            t_x = dx_phi1
            t_y = dy_phi1
            norma = pow( r_x*r_x + r_y*r_y, 1/2) * pow(t_x*t_x + t_y*t_y, 0.5)

            if ((r_x*t_x + r_y*t_y)/norma) > 1/2:
                theta1 = asin((r_x*t_y - r_y*t_x)/norma)
            elif ((r_x*t_x + r_y*t_y)/norma) < -1/2:
                #theta1 = acos((rx*tx + ry*ty)/norma)
                theta1 = pi - asin((r_x*t_y - r_y*t_x)/norma)
            else:
                theta1 = acos((r_x*t_x + r_y*t_y)/norma)
            #theta1 = acos((rx*tx + ry*ty)/norma)
        return (phi1, theta1)

    return billiard_map
