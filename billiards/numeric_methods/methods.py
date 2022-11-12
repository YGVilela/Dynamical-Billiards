from typing import Callable, List


def find_zero_newton(function: Callable[[float], List[float]], x_1: float,
                     x_2: float, acc=0.000000000001, max_iteracao=100):
    '''Implementação do método de Newton
    Aqui função retorna uma tupla f(s), f'(s)
    '''
    fl_, df_ = function(x_1)  # fl = lower, fh = higher
    fh_, df_ = function(x_2)
    if fh_ * fl_ > 0:
        raise Exception("ERRO in find_zero_Newton: root outside range")
    elif fh_ == 0:
        return x_2
    elif fl_ == 0:
        return x_1
    elif fl_ < 0:
        xl_ = x_1
        xh_ = x_2
    else:
        xh_ = x_1
        xl_ = x_2

    rts = 0.5 * (x_1 + x_2)  # Initialize the guess for root,
    dxold = abs(x_2 - x_1)  # the “stepsize before last,”
    dx_ = dxold  # and the last step.
    fff, df_ = function(rts)
    for _j in range(0, max_iteracao):  # Loop over allowed iterations.
        if (
            (((rts - xh_) * df_ - fff) * ((rts - xl_) * df_ - fff) > 0.0) or
            (abs(2.0 * fff) > abs(dxold * df_))
        ):
            # Bisect if Newton out of range,or not decreasing fast enough.
            dxold = dx_
            dx_ = 0.5 * (xh_ - xl_)
            rts = xl_ + dx_
            if xl_ == rts:
                return rts  # Change in root is negligible.
        else:  # Newton step acceptable. Take it.
            dxold = dx_
            dx_ = fff / df_
            temp = rts
            rts -= dx_
            if temp == rts:
                return rts

        if abs(dx_) < acc:
            return rts  # Convergence criterion.
        fff, df_ = function(rts)

        if fff < 0.0:
            xl_ = rts
        else:
            xh_ = rts
    return rts


def find_zero_regula_falsi(function: Callable[[float], List[float]],
                           x_1: float, x_2: float, acc=0.000000000001,
                           max_iteracao=100):
    '''Implementação do método Regula Falsi'''

    f_l, d_l = function(x_1)
    f_h, d_l = function(x_2)

    if f_h * f_l > 0:
        raise Exception("ERRO in find_zero_RegulaFalsi: root outside range")
    elif f_h == 0:
        return x_2
    elif f_l == 0:
        return x_1
    elif f_l < 0:
        x_l = x_1
        x_h = x_2
    else:
        x_h = x_1
        x_l = x_2
        swap = f_l
        f_l = f_h
        f_h = swap

    d_x = x_h - x_l

    for _j in range(max_iteracao):
        rtf = x_l + (d_x * f_l / (f_l - f_h))
        fff, ddd = function(rtf)
        if fff < 0.0:
            dif = x_l - rtf
            x_l = rtf
            f_l = fff
        else:
            dif = x_h - rtf
            x_h = rtf
            f_h = fff
        d_x = x_h - x_l
        if ((abs(dif) < acc) or (fff == 0.0)):
            return rtf

    return 0.0


def find_zero_bissec(function: Callable[[float], List[float]], x_1: float,
                     x_2: float, acc=0.0000000000001, max_iteracao=40):
    '''implementação do método da bissecção'''
    f_l, d_l = function(x_1)
    f_h, d_h = function(x_2)

    if f_h * f_l > 0:
        raise Exception("ERRO in find_zero_Bissec: root outside range")
    elif f_h == 0:
        return x_2
    elif f_l == 0:
        return x_1
    elif f_l < 0:
        x_l = x_1
        x_h = x_2
    else:
        x_h = x_1
        x_l = x_2

    for _j in range(max_iteracao):
        rts = (x_l + x_h) / 2
        dif = abs((x_h - x_l) / 2)
        if dif <= acc:
            return rts
        else:
            fff, ddd = function(rts)
            if fff == 0:
                return rts
            elif fff < 0:
                x_l = rts
            else:
                x_h = rts

    return rts
