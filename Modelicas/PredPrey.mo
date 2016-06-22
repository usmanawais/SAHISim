package PredPrey
    model PredPreyX
      // Lotka Volterra
      output Real x(start = 1);
      input Real y(start = 1);
      parameter Real alpha = 0.5;
      parameter Real beta = 0.7;
    equation
      der(x) = alpha * x - beta * x * y;
      annotation(experiment(StartTime = 0.0, StopTime = 100.0, Tolerance = 0.000001));
    end PredPreyX;

    model PredPreyY
      // Lotka Volterra
      input Real x(start = 1);
      output Real y(start = 1);
      parameter Real alpha = 0.5;
      parameter Real beta = 0.7;
      parameter Real gamma = 0.27;
      parameter Real delta = 0.6;
    equation
      der(y) = (-gamma * y) + delta * x * y;
      annotation(experiment(StartTime = 0.0, StopTime = 100.0, Tolerance = 0.000001));
    end PredPreyY;
end PredPrey;