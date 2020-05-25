# UniFract
UniFract is a fractal explorer for Ubuntu 18.04 and above.

## How to use
To use the program, just copy the code, and paste it in the Python IDE. Requires version Python 3 or above.

As long as you don't steal the code, you can use it to run this program.

## Things you can do
What you can do with the code is that you can modify the given formulas!

Just look for something like this:
```
c = pow(c, float(PowerRe)) + c0
```

Once you have found it, you can change it to any formula you want!
You can also use hybrid fractals like the following:
```
c = pow(c, float(PowerRe)) + c0
numIterations += 1

...

c = pow(np.conj(c), float(PowerRe)) + c0
numIterations += 1
```

This example combines both the Mandelbrot and Tricorn fractals.
